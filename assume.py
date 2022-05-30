import boto3
import click
import logging
import os
import yaml
from pprint import pprint
from sys import exit

# logging.basicConfig(filename='/var/log/aws_assume.log', encoding='utf-8', level=logging.ERROR)
# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.ERROR)

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
def main(shell, list):
    '''Assume AWS roles based on preconfigured information in a YAML file.
    '''

    logging.info(f"Received the args: \"{shell}\"")

    # Load the `assume` configuration file
    try:
        with open("assume.yaml", "r") as file:
            config_file = file.read()
            logging.info(f"Loaded config file!")
    except Exception as e:
        logging.error(f"File read error: \n{e}")
        exit()
    
    try:
        aliases = yaml.safe_load(config_file)
        logging.info(f"Deserialized the YAML!")
    except Exception as e:
        logging.error(f"Yaml load error: {e}")
        exit()

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



if __name__ == "__main__":
    main()