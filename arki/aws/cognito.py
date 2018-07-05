import click
import logging
from os import environ
from os.path import join
import sys
from warrant import Cognito
from arki.configs import ARKI_LOCAL_STORE_ROOT, create_ini_template, read_configs
from arki import init_logging


# Use warrant that requires AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY (otherwise use `default` profile)
ENV_AWS_ACCESS_KEY_ID = "AWS_ACCESS_KEY_ID"
ENV_AWS_SECRET_ACCESS_KEY = "AWS_SECRET_ACCESS_KEY"
for v in [ENV_AWS_ACCESS_KEY_ID, ENV_AWS_SECRET_ACCESS_KEY]:
    if v not in environ:
        logging.error(f"Environment variable {v} not set. Aborted.")
        sys.exit(1)


# Default configuration file location
ENV_STORE_FILE = join(ARKI_LOCAL_STORE_ROOT, "cognito.ini")


DEFAULT_CONFIGS = {
    "aws.cognito.userpool.appclientid": {"required": True},
    "aws.cognito.userpool.id": {"required": True},
    "aws.cognito.userpool.region": {"required": True, "default": "ap-southeast-2"},
}


def authenticate(userpool_id, userpool_appclientid, username, userpass):
    user = Cognito(userpool_id, userpool_appclientid, username=username)
    user.authenticate(password=userpass)
    return {
        "access_token": user.access_token,
        "id_token": user.id_token,
        "refresh_token": user.refresh_token,
    }


@click.command()
@click.argument("ini_file", required=False, default=ENV_STORE_FILE)
@click.option("--init", "-i", is_flag=True, help="Set up new configuration")
@click.option("--section", "-s", required=False, default="prod", help="Choices: [dev, prod], default=prod")
@click.option("--tokens", "-t", required=False, help="Return tokens for user_id:user_password")
@click.option("--list_users", "-l", is_flag=True, help="List all users of a Cognito user pool specified with `section`")
def main(ini_file, init, section, tokens, list_users):
    """
    aws_cognito supports getting tokens for a Cognito user and list all users of a User Pool.

    Use --init to create a `ini_file` with the default template to start.
    """

    try:
        init_logging()

        if init:
            create_ini_template(
                ini_file=ini_file,
                module=__file__,
                config_dict=DEFAULT_CONFIGS,
                allow_overriding_default=True
            )

        else:
            settings = read_configs(
                ini_file=ini_file,
                config_dict=DEFAULT_CONFIGS,
                section_list=[section] if section else None
            )
            userpool_id = settings["aws.cognito.userpool.id"]
            userpool_appclientid = settings["aws.cognito.userpool.appclientid"]

            if tokens:
                data = tokens.split(":")
                uname = data[0].strip().lower()
                upass = data[1].strip()

                ret_tokens = authenticate(userpool_id, userpool_appclientid, uname, upass)
                for token_name, token in ret_tokens.items():
                    print(f"{token_name}:\n{token}\n")

            if list_users:
                users = Cognito(userpool_id, userpool_appclientid).get_users()
                for user in users:
                    print(user.email)
                print(f"Total: {len(users)}")

    except Exception as e:
        logging.error(e)
        sys.exit(1)

    sys.exit(0)
