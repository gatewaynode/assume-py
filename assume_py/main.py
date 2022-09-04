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

import assume_py.config as config

# logging.basicConfig(filename='/var/log/aws_assume.log', encoding='utf-8', level=logging.ERROR)
logging.basicConfig(level=logging.DEBUG)
# logging.basicConfig(level=logging.ERROR)


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
                RoleArn=f"arn:aws:iam::{alias_data['account']}:role/{alias_data['role']}",
                RoleSessionName=f"{alias_data['alias']}-sts-session",
                ExternalId=f"{alias_data['alias']}-sts-user",
                DurationSeconds=14400,  # NOTE: Duration cannot be longer than what the assumed role supports
                Tags=[{"Key": "disposition", "Value": "assumed-role-user"}],
            )
            return sts_credentials
        except Exception as e:
            logging.error(f"Failed to assume role: \n{e}")
            exit()
    except Exception as e:
        logging.error(f"Failed to create STS client: \n{e}")
        exit()


@click.command()
@click.option(
    "--shell",
    "-s",
    help="Run from the shell wrapper accepting only the alias",
    required=False,
)
@click.option("--list", "-l", help="List aliases", is_flag=True)
@click.option(
    "--encrypt",
    "-e",
    help="Encrypt a plaintext YAML configuration file with a password.",
    is_flag=True,
)
@click.option(
    "--decrypt",
    "-d",
    help="Decrypt a ciphertext YAML configuration file with a password.",
    is_flag=True,
)
@click.argument("alias", default = "")
def main(shell, list, encrypt, decrypt, alias):
    """
    Assume AWS roles based on preconfigured information in a YAML file.
    """

    logging.info(f'Received the args: "{shell}"')

    # Load the `assume` configuration file
    config_file = config.load_config_file()
    aliases = yaml.safe_load(config_file)
    logging.info(f"Deserialized the YAML!")


    # @TODO This section is getting kind of big, time to think about moving it into it's own function
    # We try deserializing without encryption first
    if alias:
        try:
            alias_data = {}
            for item in aliases["aliases"]:
                if item["alias"] == alias:
                    alias_data = item
            if alias_data:
                # Initialize the AWS API session and call assume role for the alias
                session = aws_session()
                sts_credentials = sts_assume_role(session, alias_data)
                # Then return to the shell wrapper for injection
                print(
                    f"{sts_credentials['Credentials']['AccessKeyId']},{sts_credentials['Credentials']['SecretAccessKey']},{sts_credentials['Credentials']['SessionToken']}"
                )


        except Exception as e:
            # @TODO Enable the encypted congfig workflow
            #
            # key = input_password()
            # try:
            #     decrypted_config = decrypt_config(key, config_file)
            #     logging.info(f"Decrypted the config file!")
            #     try:
            #         aliases = yaml.safe_load(config_file)
            #         logging.info(f"Deserialized the YAML!")
            #     except Exception as e:
            #         logging.error(f"Couldn't read the decrypted config file: {e}")
            #         exit()
            # except Exception as e:
            #     logging.error(f"Couldn't read or decrypt the config file: {e}")
            #     exit()
            logging.error(f"Yaml file load error: {e}")
            exit()
    elif shell:
        alias_data = {}
        # Find the given alias in the alias file data
        for item in aliases["aliases"]:
            if item["alias"] == shell:
                alias_data = item

        if alias_data:
            logging.info(f'"{shell}" alias found: {alias_data}')

            # Initialize the AWS API session and call assume role for the alias
            session = aws_session()
            sts_credentials = sts_assume_role(session, alias_data)

            # Then return to the shell wrapper for injection
            print(
                f"{sts_credentials['Credentials']['AccessKeyId']},{sts_credentials['Credentials']['SecretAccessKey']},{sts_credentials['Credentials']['SessionToken']}"
            )
        else:
            print("Alias not found in YAML file")
            exit()
    elif list:
        for item in aliases["aliases"]:
            print(item)
    # elif encrypt:
    #     # Debugging through the process
    #     config_file = load_config_file()
    #     print("Encrypt config...")
    #     key_1 = input_password()
    #     pprint(config_file)
    #     encrypted_config = encrypt_config(key_1, config_file)
    #     pprint(encrypted_config)
    #     print("Decrypt config...")
    #     key_2 = input_password()
    #     decrypted_config = decrypt_config(key_2, encrypted_config)
    #     pprint(decrypted_config)

    # elif decrypt:
    #     pass


if __name__ == "__main__":
    main()
