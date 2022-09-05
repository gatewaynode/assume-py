"""
The AWS library to get the STS tokens.
"""

import boto3
import logging
from pprint import pprint
from sys import exit



def session():
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
