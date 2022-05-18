import click
import logging
import yaml
from pprint import pprint

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
        exit(1)
    
    try:
        aliases = yaml.safe_load(config_file)
    except Exception as e:
        logging.error(f"Yaml load error: {e}")
        exit(1)
    
    pprint(aliases)


if __name__ == "__main__":
    main()