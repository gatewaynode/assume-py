# Assume.py

An `su` like utility for the AWS CLI.

Example trust relationship policy document.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::123456789012:user/assume-user"
            },
            "Action": [
                "sts:AssumeRole",
                "sts:TagSession"
            ]
        }
    ]
}
```

Cryptography in the Python version will be provided by the [pyca/cryptography](https://cryptography.io/en/latest/) library.