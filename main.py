import boto3
import click
import logging
import os
import yaml
import subprocess
# import pipes
from pprint import pprint
from sys import exit


def aws_session():
    # @TODO Test if we already have a set of sessions vars and use them if not overriden
    try:
        session = boto3.session.Session()
        return session
    except Exception as e:
        logging.error(f"Failed to create AWS session: {e}")
        exit()

def sts_assume_role(session, alias_data):
    try:
        client = session.client("sts")
        try:
            sts_credentials = assumed_role_temporary_credentials = client.assume_role(
                RoleArn = f"arn:aws:iam::{alias_data['account']}:role/{alias_data['role']}",
                RoleSessionName = f"{alias_data['alias']}-sts-session",
                ExternalId = f"{alias_data['alias']}-sts-user",
                DurationSeconds = 43200,
                Tags = [
                    {"Key": "disposition", "Value": "assumed-role-user"}
                ]
            )
            return sts_credentials
        except Exception as e:
            logging.error(f"Failed to assume role: {e}")
            exit()
    except Exception as e:
        logging.error(f"Failed to create STS client: {e}")
        exit()
    
    

@click.command()
@click.argument("alias")
@click.option("--exit", "-x", help="Remove assumed roles from environment")
@click.option("--list", "-l", help="List aliases")
def main(alias, exit, list):
    '''Assume AWS roles based on preconfigured information in a YAML file.
    '''
    try:
        with open("EXAMPLE.assume.yaml", "r") as file:
            config_file = file.read()
            logging.warning(f"Loaded from file = \n{config_file}")
    except Exception as e:
        logging.error(f"File read error: {e}")
        exit()
    
    try:
        aliases = yaml.safe_load(config_file)
    except Exception as e:
        logging.error(f"Yaml load error: {e}")
        exit()

    alias_data = {}
    for item in aliases["aliases"]:
        if item["alias"] == alias:
            alias_data = item

    if alias_data:
        pprint(alias_data)
        # session = aws_session() # Works
        # sts_credentials = sts_assume_role(session, alias_data) # Works
        subprocess.run([f"export TESTING={alias_data['alias']}"], shell=True)
        # print(f"export TESTING={alias_data['alias']}\n")
        # @BUG Eh, maybe just swap around things in the credentials file.
    else:
        print("Alias not found in YAML file")
        exit()



if __name__ == "__main__":
    main()