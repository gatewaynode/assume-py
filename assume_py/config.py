import logging
import os
import yaml
import base64
import hashlib
from cryptography.fernet import Fernet
from pprint import pprint
from sys import exit



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
        # key = click.prompt("Enter your password: ", type=str)
        # config_plaintext = decrypt_string(key, config_file)
        logging.error(f"Yaml load error: {e}")
        exit()


def input_password():
    """
    Take a hidden user input string, SHA256 hash it, and URL safe base64 encode it.
    """
    password = click.prompt(
        "Enter your password: ", hide_input=True, show_default=False, type=str
    )
    hash = hashlib.sha256()
    hash.update(bytes(password, "utf-8"))
    key = base64.urlsafe_b64encode(hash.digest())
    return key


def decrypt_config(key, cipher_text):
    """
    This function takes a config file var, `cipher_text` (which is in bytes), and a decryption
    key, `key` (which is a string) and attempts to decrypt the file contents to a byte string
    which can then be deserialized.
    """
    client = Fernet(key)
    try:
        plaintext_bytes = client.decrypt(cipher_text)
        try:
            plaintext = plaintext_bytes.decode("utf-8")
            return plaintext
        except Exception as e:
            logging.error(f"Could not decode the decryption result as UTF-8: {e}")
            exit()
    except Exception as e:
        logging.error(f"String decryption failed: {e}")
        exit()


def encrypt_config(key, plain_text):
    client = Fernet(key)
    try:
        cipher_text = client.encrypt(bytes(plain_text, "utf-8"))
        return cipher_text
    except Exception as e:
        logging.error(f"String encryption failed: {e}")
        exit()


