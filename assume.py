"""
This is the prototyping variant of assume, which is used to alias AWS assumed roles in an easy to use 
command line utility.
"""

import boto3
import click
import logging
import os
import yaml
import base64
import hashlib
from cryptography.fernet import Fernet
from pprint import pprint
from sys import exit

# logging.basicConfig(filename='/var/log/aws_assume.log', encoding='utf-8', level=logging.ERROR)
# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.ERROR)



def load_config_file():
    """
    This simple loads the configuration YAML file.  In this prototype it is assumed it is in the
    source code directory.
    """
    try:
        with open("assume.yaml", "r") as file:
            config_file = file.read()
            logging.info(f"Loaded config file!")
            return config_file
    except Exception as e:
        logging.error(f"File read error: \n{e}")
        exit()

def write_config_file(config_file):
    """
    This writes the existing in memory configuration to the persistent configuration file.  This
    also assumes the configuration fir is in the source code directory.
    """
    try:
        with open("assume.yaml", "w") as file:
            file.write(config_file)
            logging.info(f"Wrote config file!")
    except Exception as e:
        logging.error(f"File read error: \n{e}")
        exit()

def read_config(config_file):
    """
    After loading the configuration file it is deserialized from YAML to Python native vars. 

    In this case we try deserializing without encryption first, if that fails then we attempt
    to decrypt the file by asking for a password.
    """
    try:
        aliases = yaml.safe_load(config_file)
        logging.info(f"Deserialized the YAML!")
        return aliases
    except Exception as e:
        # If deserialization fails, then ask for a password and try to decrypt
        key = click.prompt("Enter your password: ", type = str)
        config_plaintext = decrypt_string(key, config_file)
        # logging.error(f"Yaml load error: {e}")
        # exit()

def decrypt_config(key, cipher_text):
    """
    This function takes a config file var, `cipher_text` (which is in bytes), and a decryption 
    key, `key` (which is a string) and attempts to decrypt the file contents to a byte string 
    which can then be deserialized.
    """
    client = Fernet(key)
    try:
        plaintext = client.decrypt(cipher_text)
        return plaintext
    except Exception as e:
        logging.error(f"String decryption failed: {e}")

def encrypt_config(key, plain_text):
    client = Fernet(key)
    try:
        cipher_text = client.encrypt(plain_text)
    except Exception as e:
        logging.error(f"String encryption failed: {e}")

def aws_session():
    """
    A simple function to set our AWS API session from existing credentials
    """
    # @TODO Test if we already have a set of sessions vars and use them if not overriden
    try:
        session = boto3.session.Session()
        return session
    except Exception as e:
        logging.error(f"Failed to create AWS session: {e}")
        exit()

def sts_assume_role(session, alias_data):
    """
    Using the AWS API session run the STS assume role operation and return the response.
    """
    try:
        client = session.client("sts")
        try:
            sts_credentials = assumed_role_temporary_credentials = client.assume_role(
                RoleArn = f"arn:aws:iam::{alias_data['account']}:role/{alias_data['role']}",
                RoleSessionName = f"{alias_data['alias']}-sts-session",
                ExternalId = f"{alias_data['alias']}-sts-user",
                DurationSeconds = 14400, # NOTE: Duration cannot be longer than what the assumed role supports
                Tags = [
                    {"Key": "disposition", "Value": "assumed-role-user"}
                ]
            )
            return sts_credentials
        except Exception as e:
            logging.error(f"Failed to assume role: \n{e}")
            exit()
    except Exception as e:
        logging.error(f"Failed to create STS client: \n{e}")
        exit()

@click.command()
@click.option("--shell", "-s", help="Run from the shell wrapper accepting only the alias", required=False)
@click.option("--list", "-l", help="List aliases", is_flag=True)
@click.option("--encrypt", "-e", help="Encrypt a plaintext YAML configuration file with a password.", is_flag=True)
@click.option("--decrypt", "-d", help="Decrypt a ciphertext YAML configuration file with a password.", is_flag=True)
def main(shell, list, encrypt, decrypt):
    '''
    Assume AWS roles based on preconfigured information in a YAML file.
    '''

    logging.info(f"Received the args: \"{shell}\"")

    # Load the `assume` configuration file
    config_file = load_config_file()
    
    # We try deserializing without encryption first
    try:
        aliases = yaml.safe_load(config_file)
        logging.info(f"Deserialized the YAML!")
    except Exception as e:
        key = click.prompt("Enter your password: ", type = str)
        # logging.error(f"Yaml load error: {e}")
        # exit()

    if shell:
        alias_data = {}
        # Find the given alias in the alias file data
        for item in aliases["aliases"]:
            if item["alias"] == shell:
                alias_data = item

        if alias_data:
            logging.info(f"\"{shell}\" alias found: {alias_data}")
            
            # Initialize the AWS API session and call assume role for the alias
            session = aws_session()
            sts_credentials = sts_assume_role(session, alias_data)
            
            # Then return to the shell wrapper for injection
            print(f"{sts_credentials['Credentials']['AccessKeyId']},{sts_credentials['Credentials']['SecretAccessKey']},{sts_credentials['Credentials']['SessionToken']}")
        else:
            print("Alias not found in YAML file")
            exit()
    elif list:
        for item in aliases["aliases"]:
            print(item)
    elif encrypt:
        config_file = load_config_file()
        hash = hashlib.sha256()
        hash.update(b'THIS_IS_A_TEST')
        key = base64.urlsafe_b64encode(hash.digest())
        encrypted_config = encrypt_config(key, config_file) # Only accepts bytes, not strings apparently
        pprint(encrypt_config)

    elif decrypt:
        pass


if __name__ == "__main__":
    main()