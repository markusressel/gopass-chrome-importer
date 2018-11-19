#!/usr/bin/env python3

import click
import subprocess
import re
import os

from enum import Enum

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


@click.group()
def cli():
    pass


@cli.command(name="import")
@click.option('-path', '-p', required=True, type=str, help='Path to the chrome password export .csv file.')
@click.option('-gopass-subpath', '-gp', required=False, type=str, default="imported/",
              help='The path in gopass where all entries are imported to.')
@click.option('-f', '--force', required=False, default=False, is_flag=True,
              help='When set existing passwords will be overwritten. USE WITH CAUTION!')
@click.option('--yes', required=False, default=False, is_flag=True,
              help='When set no questions will be asked during execution. '
                   'This effectively sets the --yes flag on gopass. '
                   'Note that this will NOT overwrite any existing data (see "-f" to do that)')
@click.option('--dry-run', required=False, default=False, is_flag=True,
              help='When set no passwords will actually be written and a preview of what WOULD be done will be printed.')
def c_import(path: str, gopass_subpath: str, force: bool, yes: bool, dry_run: bool):
    """Imports all items in the chrome password export"""

    entries = _read_csv(path)

    for entry in entries:

        if entry["name"]:
            site = _format_site(entry["name"])
        else:
            site = _format_site(entry["url"])

        if entry["username"]:
            user = entry["username"]
        else:
            # TODO: generate username that will never collide with an existing one
            rolling_counter_for_website = 0
            user = "site_pw_%s" % rolling_counter_for_website

        secret_path = "%s%s/%s" % (gopass_subpath, site, user)
        password = entry["password"]

        # this command is a simple workaround to use gopass in a non-interactive way
        # by using the edit command and a 'fake' editor that is this python script and
        # stores the password in the temporarily decrypted file until
        # gopass encrypts it.

        # store username in an env variable
        os.environ[USERNAME_ENV_VARIABLE_NAME] = user
        # store password in an env variable
        os.environ[PASSWORD_ENV_VARIABLE_NAME] = password

        # set custom "editor" that will process the password
        editor_command = "python3 gopass-chrome-importer.py store"
        if force:
            editor_command += " -f"
        if dry_run:
            editor_command += " --dry-run"
        os.environ[EDITOR_ENV_VARIABLE_NAME] = editor_command

        # append the actual gopass command
        gopass_command = "gopass"
        if yes:
            gopass_command += " --yes"
        gopass_command += " edit '%s'" % secret_path

        # execute the command
        if dry_run:
            click.echo("Would import: %s" % secret_path)
        _run_shell_command(gopass_command)

    click.echo("Done.")


@cli.command(name="store")
@click.argument('filepath', required=True, type=str)
@click.option('-f', "--force", required=False, default=False, is_flag=True,
              help='When set to true existing passwords will be overwritten. USE WITH CAUTION!')
@click.option('--dry-run', required=False, default=False, is_flag=True,
              help='When set no passwords will actually be written and a preview of what WOULD be done will be printed.')
def c_store(filepath: str, force: bool, dry_run: bool):
    """
    Stores a password in the given file path.
    As it could be security critical to pass a password as a command line parameter this method uses an environment variable
    instead called "GOPASS_STORE_PASS"

    """

    # check if the file is empty
    statinfo = os.stat(filepath)
    if statinfo.st_size is not 0:
        if not force:
            click.echo(click.style("Non-empty file will NOT be overridden: %s" % filepath, fg='yellow'))
            return
        else:
            click.echo(click.style("Non-empty file WILL BE overridden: %s" % filepath, fg='yellow'))

    username = os.environ[USERNAME_ENV_VARIABLE_NAME]
    password = os.environ[PASSWORD_ENV_VARIABLE_NAME]

    if dry_run:
        text_to_write = '*' * len(password)
    else:
        text_to_write = password

    if username:
        text_to_write += "\n---\n"
        text_to_write += "user: %s" % username

    if dry_run:
        click.echo(text_to_write + '\n')
    else:
        with open(filepath, 'w') as file:
            file.write(text_to_write)


if __name__ == '__main__':
    cli()