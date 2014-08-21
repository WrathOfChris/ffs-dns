from flask import Flask, render_template
import dns.resolver
import json
import random
import shlex
import socket
import time
featureflag = Flask(__name__)

FF_DOMAIN = 'ff.example.com'
FF_DISABLED = '127.0.0.0'
FF_ENABLED = '127.0.0.1'
FF_GROUP = 'group'
FF_RANDOM = 'random'
FF_LIST = ['my-feature', 'my-feature-no', 'my-simplefeature']

@featureflag.route('/')
def route_index():
    return render_template('feature.j2', features=FF_LIST)

@featureflag.route("/feature/<feature>")
def route_feature(feature):
    answer = {}
    answer['feature'] = feature
    answer['enabled'] = False
    f_name = feature + '.' + FF_DOMAIN

    #
    # Feature:
    #   127.0.0.0 - disabled
    #   127.0.0.1 - enabled
    #

    try:
        d_addr = dns.resolver.query(f_name, 'A')
    except dns.resolver.NXDOMAIN:
        # feature flag not found
        answer['expiration'] = time.time()
        return json.dumps(answer), 404
    except dns.resolver.Timeout:
        # request timeout
        answer['expiration'] = time.time()
        return json.dumps(answer), 408
    except dns.exception.DNSException:
        # other exception
        answer['expiration'] = time.time()
        return json.dumps(answer), 500

    if len(d_addr.rrset) > 0:
        if d_addr.rrset[0].to_text() == FF_ENABLED:
            answer['enabled'] = True
        answer['expiration'] = d_addr.expiration

    #
    # Feature Statements:
    #   group=
    #   random=%
    #   flag
    #

    try:
        d_txt = dns.resolver.query(f_name, 'TXT')
    except dns.resolver.NoAnswer:
        # no additional statements
        return json.dumps(answer)
    except dns.exception.DNSException:
        # other exception
        return json.dumps(answer), 500

    for t in d_txt.response.answer:
        for i in t.items:
            txtrec = i.to_text()

            # TXT records should be quoted ""
            if txtrec.startswith('"') and txtrec.endswith('"'):
                txtrec = txtrec[1:-1]

            # Map each statement
            stmts = shlex.split(txtrec)
            for stmt in stmts:
                (s,sep,v) = stmt.partition('=')

                # statements without values are flag atoms
                if sep != '=':
                    if 'flags' not in answer:
                        answer['flags'] = list()
                    answer['flags'].append(s)
                    continue

                if s == FF_GROUP:
                    if 'groups' not in answer:
                        answer['groups'] = list()
                    groups = v.split(',')
                    for g in groups:
                        answer['groups'].append(g)

                if s == FF_RANDOM:
                    if 'random' not in answer:
                        answer['random'] = {}
                    randval = v.strip('%')
                    answer['random']['percent'] = randval
                    if random.randint(0, 100) < int(randval):
                        answer['random']['success'] = True
                    else:
                        answer['random']['success'] = False
    return json.dumps(answer)

# Enable Flask Debug
featureflag.config.update(
        DEBUG=True,
        )

if __name__ == '__main__':
    # Kick off the flask
    featureflag.run()
