import logging
import os
import yaml
import base64
import hashlib
from cryptography.fernet import Fernet
from pprint import pprint
from sys import exit
from xdg import xdg_config_home as xdg_c
from pathlib import Path



def find_or_create_config_file():
    """
    This function insures that we have a configuration file to work with as storage.  If it doesn't
    exist, we'll create the directory for it and write the default value.
    """
    
    DEFAULT_CONF = """---
aliases:
  - alias: "bob"
    account: 123456789012
    role: "bucket-creator"
    description: "This is a sample S3 user role, description is for user purposes only."
  - alias: "laura"
    account: 123456789012
    role: "lambda-creator"
    description: "This is a sample lambda creator, description is for user purposes only."
"""

    conf_path = Path(f"{xdg_c()}/assume/assume.conf")
    logging.info(f"Configuration path: {conf_path}")
    if conf_path.is_file():
        return conf_path
    else:
        logging.info(f"Config not found, trying to create: {conf_path}")
        conf_dir = conf_path = Path(f"{xdg_c()}/assume")
        if conf_dir.is_dir():
            try:
                with open(conf_path, "w") as file:
                    file.write(DEFAULT_CONF)
            except Exception as e:
                logging.error(f"Could not create config file: {conf_path}\n{e}")
                exit()
        else:
            try:
                os.makedirs(f"{xdg_c()}/assume")
                try:
                    with open(conf_path, "w") as file:
                        file.write(DEFAULT_CONF)
                except Exception as e:
                    logging.error(f"Could not create config file: {conf_path}\n{e}")
                    exit()
            except Exception as e:
                logging.error(f"Could not create config file dir: {conf_path}\n{e}")
                exit()


def load_config_file(conf_path):
    """
    This simple loads the configuration YAML file.  In this prototype it is assumed it is in the
    source code directory.
    """
    logging.info(f"Reading conf from path: {conf_path}")
    try:
        with open(conf_path, "r") as file:
            config_data = yaml.load(file, Loader=yaml.SafeLoader)
            logging.info(f"Loaded and deserialized the config file!")
            return config_data
    except Exception as e:
        logging.error(f"File read error: \n{e}")
        exit()
        # @TODO Encrypted workflow goes here
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



def write_config_file(config, config_path):
    """
    This writes the existing in memory configuration to the persistent configuration file.
    """
    try:
        with open(config_path, "w") as file:
            yaml.dump(config, file)
            logging.info(f"Wrote config file!")
    except Exception as e:
        logging.error(f"File read error: \n{e}")
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


