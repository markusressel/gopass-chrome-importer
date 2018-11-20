#!/usr/bin/env python3

import os
import subprocess
from enum import Enum

import click

SECRET_PATH_ENV_VARIABLE_NAME = 'GOPASS_STORE_SECRET_PATH'
USERNAME_ENV_VARIABLE_NAME = 'GOPASS_STORE_USER'
PASSWORD_ENV_VARIABLE_NAME = 'GOPASS_STORE_PASS'
EDITOR_ENV_VARIABLE_NAME = 'EDITOR'
IPV4_REGEX = "(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"


class UrlType(Enum):
    ANDROID = "android"
    IP = "ip"
    DOMAIN = "domain"


def _run_shell_command(cmd: str, run_as: str = None) -> None:
    """Run a shell command"""
    if run_as is not None:
        cmd = "sudo -u %s %s" % (run_as, cmd)

    result = subprocess.call(cmd, shell=True)
    if result is not 0:
        raise ValueError("An error occurred")


def _read_csv(path: str) -> [dict]:
    """
    Parses a chrome password export csv file to a list

    :param path: the path of the csv file
    :return: file parsed to a list
    """
    import csv

    result = []

    with open(path) as file:
        reader = csv.reader(file, delimiter=',')
        for row in reader:
            result.append({
                "name": row[0],
                "url": row[1],
                "username": row[2],
                "password": row[3]
            })

    return result


def _find_type(url: str) -> UrlType:
    """
    Checks the type of url, f.ex. a normal website, an IP Address or an android app specific url
    :param url:
    :return:
    """

    import re

    if url.startswith("android://"):
        return UrlType.ANDROID
    elif re.match(IPV4_REGEX, url):
        return UrlType.IP
    else:
        return UrlType.DOMAIN


def _format_site(url: str) -> str:
    """
    Formats a url to
    """

    url_type = _find_type(url)

    result = url
    if url_type is UrlType.IP or url_type is UrlType.DOMAIN:
        result = result.replace('https://', '')
        result = result.replace('http://', '')
        result = result.replace('www.', '')

        if url_type is UrlType.IP:
            result = "ip/" + result
        else:
            result = "website/" + result

    if url_type is UrlType.ANDROID:
        import re
        # strip away everything except app package name
        matches = re.search("(?:==@)([\w\d.]*)", result)
        if not matches:
            click.echo("No match found: %s" % url, err=True)
            exit(1)

        result = "android/" + matches.group(1)

    return result


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    pass


@cli.command(name="import")
@click.option('--path', '-p', required=True, type=str, help='Path to the chrome password export .csv file.')
@click.option('--gopass-basepath', '-gb', required=False, type=str, default="imported/",
              help='The path in gopass where all entries are imported to.')
@click.option('--force', '-f', required=False, default=False, is_flag=True,
              help='When set existing passwords will be overwritten. USE WITH CAUTION!')
@click.option('--yes', '-y', required=False, default=False, is_flag=True,
              help='When set no questions will be asked during execution. '
                   'This effectively sets the --yes flag on gopass. '
                   'Note that this will NOT overwrite any existing data (see "-f" to do that)')
@click.option('--dry-run', '-d', required=False, default=False, is_flag=True,
              help='When set no passwords will actually be written and a preview of what WOULD be done will be printed.')
def c_import(path: str, gopass_basepath: str, force: bool, yes: bool, dry_run: bool):
    """Imports items from a chrome password export"""

    # set custom "editor" that will process the password
    editor_command = "gopass-chrome-importer store_internal"
    if force:
        editor_command += " -f"
    if dry_run:
        editor_command += " --dry-run"
    os.environ[EDITOR_ENV_VARIABLE_NAME] = editor_command

    entries = _read_csv(path)

    for entry in entries:
        if entry["name"]:
            site = _format_site(entry["name"])
        else:
            site = _format_site(entry["url"])

        if entry["username"]:
            user = entry["username"]
        else:
            user = "site_pw"

        secret_path = "%s%s/%s" % (gopass_basepath, site, user)
        password = entry["password"]

        # this command is a simple workaround to use gopass in a non-interactive way
        # by using the edit command and a 'fake' editor that is this python script and
        # stores the password in the temporarily decrypted file until
        # gopass encrypts it.

        # store final path to the secret in an env variable
        os.environ[SECRET_PATH_ENV_VARIABLE_NAME] = secret_path
        # store username
        os.environ[USERNAME_ENV_VARIABLE_NAME] = user
        # store password
        os.environ[PASSWORD_ENV_VARIABLE_NAME] = password

        # append the actual gopass command
        gopass_command = "gopass"
        if yes:
            gopass_command += " --yes"
        gopass_command += " edit '%s'" % secret_path

        _run_shell_command(gopass_command)

    click.echo("Done.")


@cli.command(name="store_internal", hidden=True)
@click.argument('file_path', required=True, type=str)
@click.option("--force", '-f', required=False, default=False, is_flag=True,
              help='When set to true existing passwords will be overwritten. USE WITH CAUTION!')
@click.option('--dry-run', '-d', required=False, default=False, is_flag=True,
              help='When set no passwords will actually be written and a preview of what WOULD be done will be printed.')
def c_store_internal(file_path: str, force: bool, dry_run: bool):
    """
    NOTE: This is an internal command and not meant to be used from outside.
    Stores a password in the given file path.

    As it could be security critical to pass a password as a command line parameter this method uses
    an environment variable instead.
    """

    final_secret_path = os.environ[SECRET_PATH_ENV_VARIABLE_NAME]

    # check if the file is empty
    file_stats = os.stat(file_path)
    if file_stats.st_size is not 0:
        if not force:
            click.echo(click.style("Non-empty file will NOT be overwritten: %s" % final_secret_path, fg='yellow'))
            return
        else:
            click.echo(click.style("Non-empty file WILL BE overwritten: %s" % final_secret_path, fg='yellow'))

    username = os.environ[USERNAME_ENV_VARIABLE_NAME]
    password = os.environ[PASSWORD_ENV_VARIABLE_NAME]

    if dry_run:
        text_to_write = "Would import: %s\n" % final_secret_path
        text_to_write += '*' * len(password)
    else:
        text_to_write = password

    if username:
        text_to_write += "\n---\n"
        text_to_write += "user: %s" % username

    if dry_run:
        # just print what would be executed
        click.echo(text_to_write + '\n')
    else:
        with open(file_path, 'w') as file:
            file.write(text_to_write)


if __name__ == '__main__':
    cli()
