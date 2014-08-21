ffs-dns
=======

feature flag service based on DNS

### feature flag test

```
cd files
python feature.py
```

In your web browser: [link](http://localhost:5000/)

API returns 408 on timeout, 500 on DNS failure.

### Simple Feature:
Returns: 200

```
{
    "enabled": true,
    "feature": "my-simplefeature",
    "expiration": 1400613356.884319
}
```

### Feature with statements
Returns: 200

```
{
    "random":
    {
        "percent": "10",
        "success": false
    },
    "enabled": true,
    "feature": "my-feature",
    "flags": ["flag"],
    "expiration": 1400613259.880848,
    "groups": [ "mygroup1", "mygroup2" ]
}
```

### Non-existent feature
Returns: 404

```
{
    "enabled": false,
    "feature": "my-feature-no",
    "expiration": 1400613185.638841
}
```
