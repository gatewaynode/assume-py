import boto3
import click
import logging
import yaml
from pprint import pprint


def aws_session():
    # @TODO Test if we already have a set of sessions vars and use them if not overriden
    try:
        session = boto3.session.Session()
        return session
    except Exception as e:
        logging.error(f"Failed to create AWS session: {e}")
        exit()

def sts_assume_role(session, alias):
    try:
        client = session.client("s3")
        try:
            # assumed_role_temporary_credentials = client.
            pass
        except Exception as e:
            logging.error(f"Failed to assume role: {e}")
    except Exception as e:
        logging.error(f"Failed to create STS client: {e}")
    
    

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
    else:
        print("Alias not found in YAML file")
        exit()



if __name__ == "__main__":
    main()