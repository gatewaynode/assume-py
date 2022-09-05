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
import assume_py.aws as aws

# logging.basicConfig(filename='/var/log/aws_assume.log', encoding='utf-8', level=logging.ERROR)
logging.basicConfig(level=logging.DEBUG)
# logging.basicConfig(level=logging.ERROR)


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
    conf_path = config.find_or_create_config_file()
    config_data = config.load_config_file(conf_path)


    # @TODO This section is getting kind of big, time to think about moving it into it's own function
    # We try deserializing without encryption first
    if config_data and alias:
        try:
            alias_data = {}
            for item in config_data["aliases"]:
                if item["alias"] == alias:
                    alias_data = item
            if alias_data:
                # Initialize the AWS API session and call assume role for the alias
                session = aws.session()
                sts_credentials = aws.sts_assume_role(session, alias_data)
                # Then return to the shell wrapper for injection
                print(
                    f"{sts_credentials['Credentials']['AccessKeyId']},{sts_credentials['Credentials']['SecretAccessKey']},{sts_credentials['Credentials']['SessionToken']}"
                )
        except Exception as e:
            logging.error(f"Yaml file load error: {e}")
            exit()
    elif shell:
        alias_data = {}
        # Find the given alias in the alias file data
        for item in config_data["aliases"]:
            if item["alias"] == shell:
                alias_data = item

        if alias_data:
            logging.info(f'"{shell}" alias found: {alias_data}')

            # Initialize the AWS API session and call assume role for the alias
            session = aws.session()
            sts_credentials =aws.sts_assume_role(session, alias_data)

            # Then return to the shell wrapper for injection
            print(
                f"{sts_credentials['Credentials']['AccessKeyId']},{sts_credentials['Credentials']['SecretAccessKey']},{sts_credentials['Credentials']['SessionToken']}"
            )
        else:
            print("Alias not found in YAML file")
            exit()
    elif list:
        for item in config_data["aliases"]:
            print(item)


if __name__ == "__main__":
    main()
