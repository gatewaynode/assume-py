# Assume.py

An `su` like utility for the AWS CLI.

## Description

This is a utilty designed for use with the AWS CLI.  It provides a simeple way to assume different roles in your AWS CLI session.  It does this by referencing a configuration file that contains the details of  different roles you can assume from your base credentialled user.  The temporary credentials provided by the secure token service are injected into your shell session as environment variables which will override those provided by your credentials file.  This let's you create minimally permitted users who can then  easily change to different roles, or "exit" by setting the env vars to "".

## Installation

This is pretty manual right now, requiring either the virtual env or manually installing the requirements.

1. Install the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
2. Create an alias to the main Python file in your `~/.local/bin` directory

```bash
$ pwd
/user/USERNAME/.local/bin
$ ln -s ASSUME_REPO_LOCATION/assume.py
$ ls -la assume.py 
lrwxrwxrwx anon anon 46 B Sun May 29 07:55:56 2022  assume.py ⇒ /home/USERNAME/ASSUME_REPO_LOCATION/assume-py/assume.py
```

3. Create an alias to the shell script wrapper file in your `~/.local/bin` directory

```bash
$ pwd
/user/USERNAME/.local/bin
$ ln -s ASSUME_REPO_LOCATION/assume_wrapper.bash
$ ls -la assum*
lrwxrwxrwx anon anon 46 B Sun May 29 07:55:56 2022  assume.py ⇒ /home/USERNAME/ASSUME_REPO_LOCATION/assume-py/assume.py
lrwxrwxrwx anon anon 56 B Mon May 30 08:53:12 2022  assume_wrapper.bash ⇒ /home/USERNAME/ASSUME_REPO_LOCATION/aassume-py/assume_wrapper.bash
```

4. Add the alias from `assume_alias.bash` to your `.bashrc` or `.bash_aliases`(if you use that file).
5. Use `source` to load the file with the alias in your current environment.
6. Create and activate your virtual environment (not necessary if you installed the requirements.txt to your system)

Locally this should be working, but since this is an AWS tool you'll need to create the user, user permissions and a role to assume into on AWS.  Below is an example of the trust policy doc but the rest is a little too involved for this right now.  There might be some CloudFormation auto-setup for this in the roadmap, but it's beyond the scope of this currently.

## Usage

The idea of this utility is to make the whole process simple, so if you have an alias in your assume.yaml file for an S3 permission set and you named it "bob", you could do this on the CLI.

```bash
(env) anon@box:/home/USERNAME/ASSUME_REPO_LOCATION/assume-py$ assume whoami
{
    "UserId": "EXAMPLE111AAAABBBBCCC",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/assume-dev"
}
(env) anon@box:/home/USERNAME/ASSUME_REPO_LOCATION/assume-py$ assume bob
(env) anon@box:/home/USERNAME/ASSUME_REPO_LOCATION/assume-py$ assume whoami
{
    "UserId": "EXAMPLE222DDDEEEFFF:bob-sts-session",
    "Account": "123456789012",
    "Arn": "arn:aws:sts::123456789012:assumed-role/elevated_s3_access/bob-sts-session"
}
(env) anon@box:/home/USERNAME/ASSUME_REPO_LOCATION/assume-py$ assume exit
(env) anon@box:/home/USERNAME/ASSUME_REPO_LOCATION/assume-py$ assume whoami
{
    "UserId": "EXAMPLE111AAAABBBBCCC",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/assume-dev"
}

```

## AWS Setup

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

# Threat Model

By setting minimally permissioned, persistent user credentials we can deal with several threats that are currently handled in ways that cause a lot of friction with CLI interactions in AWS.  So let's go over them:
 
1. Credentials Leaked in Code
2. Supply Chain Credential Theft
3. Developer/Operations Workstation Remote Compromise
4. Developer/Operations Workstation Local Compromise

# Appendix
Cryptography in the Python version will be provided by the [pyca/cryptography](https://cryptography.io/en/latest/) library.
