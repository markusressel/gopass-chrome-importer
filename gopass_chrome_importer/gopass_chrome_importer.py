#!/usr/bin/env python3

import os
import subprocess
from enum import Enum

import click

from gopass_chrome_importer.summary.summary_manager import SummaryManager

SUMMARY_TMP_FILE_ENV_VARIABLE_NAME = 'GOPASS_CHROME_IMPORTER_SUMMARY_TMP_FILE_PATH'
SECRET_PATH_ENV_VARIABLE_NAME = 'GOPASS_CHROME_IMPORTER_STORE_SECRET_PATH'
USERNAME_ENV_VARIABLE_NAME = 'GOPASS_CHROME_IMPORTER_STORE_USER'
PASSWORD_ENV_VARIABLE_NAME = 'GOPASS_CHROME_IMPORTER_STORE_PASS'
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

    :param url: the url to analyze
    :return: the type of the url to insert
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
    Formats the given URL for the use as a secret file name

    :param url: The URL to format
    :return: the formatted name
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
        matches = re.search(r"(?:==@)([\w\d.]*)", result)
        if not matches:
            echo("No match found: %s" % url, err=True)
            exit(1)

        result = "android/" + matches.group(1)

    return result


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

CMD_STORE_INTERNAL = "store_internal"

PARAM_PATH = "path"
PARAM_GOPASS_PATH = "gopass-path"
PARAM_FORCE = "force"
PARAM_YES = "yes"
PARAM_DRY_RUN = "dry-run"

CMD_OPTION_NAMES = {
    PARAM_PATH: ['--path', '-p'],
    PARAM_GOPASS_PATH: ['--gopass-basepath', '-gb'],
    PARAM_FORCE: ['--force', '-f'],
    PARAM_YES: ['--yes', '-y'],
    PARAM_DRY_RUN: ['--dry-run', '-d']
}

SUMMARY_MANAGER = SummaryManager()


@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    pass


def get_option_names(parameter: str) -> list:
    """
    Returns a list of all valid console parameter names for a given parameter
    :param parameter: the parameter to check
    :return: a list of all valid names to use this parameter
    """
    return CMD_OPTION_NAMES[parameter]


@cli.command(name="import")
@click.option(*get_option_names(PARAM_PATH), required=True, type=str,
              help='Path to the chrome password export .csv file.')
@click.option(*get_option_names(PARAM_GOPASS_PATH), required=False, type=str, default="imported/",
              help='The path in gopass where all entries are imported to.')
@click.option(*get_option_names(PARAM_FORCE), required=False, default=False, is_flag=True,
              help='When set existing passwords will be overwritten. USE WITH CAUTION!')
@click.option(*get_option_names(PARAM_YES), required=False, default=False, is_flag=True,
              help='When set no questions will be asked during execution. '
                   'This effectively sets the --yes flag on gopass. '
                   'Note that this will NOT overwrite any existing data (see "-f" to do that)')
@click.option(*get_option_names(PARAM_DRY_RUN), required=False, default=False, is_flag=True,
              help='When set no passwords will actually be written and a preview of what WOULD be done will be printed.')
def c_import(path: str, gopass_basepath: str, force: bool, yes: bool, dry_run: bool):
    """
    Imports items from a chrome password export

    :param path: Path to the chrome password export .csv file
    :param gopass_basepath: The base path to insert secrets into within gopass
    :param force: If set to True existing secrets will be overwritten by imported data
    :param yes: Automatically answer to gopass requests with "yes" if applicable (see gopass documentation)
    :param dry_run: If set to True no changes will be made to the gopass store
    """

    # set custom "editor" that will process the password
    editor_command = "gopass-chrome-importer %s" % CMD_STORE_INTERNAL
    if force:
        editor_command += " %s" % get_option_names(PARAM_FORCE)[0]
    if dry_run:
        editor_command += " %s" % get_option_names(PARAM_DRY_RUN)[0]
    os.environ[EDITOR_ENV_VARIABLE_NAME] = editor_command

    # set path to summary tmp file used for this run
    os.environ[SUMMARY_TMP_FILE_ENV_VARIABLE_NAME] = SUMMARY_MANAGER.get_tmp_file_path()

    entries = _read_csv(path)

    for entry in entries:
        if entry.get("name") == "name" and entry.get("url") == "url" and entry.get(
                "username") == "username" and entry.get("password") == "password":
            # this is the header of the csv file and can be ignored
            # it would be possible to just ignore the first line of the csv
            # but you never know wo might think it's a good idea to delete that...
            continue

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
        gopass_command += " edit"

        # TODO: maybe we could use this to be able to only update existing secrets, without creating new ones
        # dont know if this is an actual usecase though...
        create_new = True
        if create_new:
            gopass_command += " --create"

        gopass_command += " '%s'" % secret_path

        _run_shell_command(gopass_command)

    SUMMARY_MANAGER.print_summary()


def _create_secret_content(username: str or None, password: str, mask_pw: bool = False) -> str:
    """
    Creates the text that is written to a secret

    :param username: a username, if present
    :param password: the password
    :param mask_pw: when set to true the password will be masked
    :return: the secret file content
    """
    if mask_pw:
        content = len(password) * '*'
    else:
        content = password

    if username:
        content += "\n---\n"
        content += "user: %s" % username

    return content


def echo(text: str, info: bool = False, warn: bool = False, err: bool = False) -> None:
    """
    Simple wrapper for the click.echo function

    :param text: the text to print
    :param info: set to true, when this is a info message
    :param warn: set to true, when this is a warning message
    :param err: set to true, when this is an error message
    """

    if info:
        foreground_color = 'green'
    elif warn:
        foreground_color = 'yellow'
        SUMMARY_MANAGER.add_warning(text)
    elif err:
        foreground_color = 'red'
        SUMMARY_MANAGER.add_error(text)
    else:
        foreground_color = 'white'

    click.echo(click.style(text, fg=foreground_color), err=err)


@cli.command(name=CMD_STORE_INTERNAL, hidden=True)
@click.argument('file_path', required=True, type=str)
@click.option(*get_option_names(PARAM_FORCE), required=False, default=False, is_flag=True,
              help='When set to true existing passwords will be overwritten. USE WITH CAUTION!')
@click.option(*get_option_names(PARAM_DRY_RUN), required=False, default=False, is_flag=True,
              help='When set no passwords will actually be written and a preview of what WOULD be done will be printed.')
def c_store_internal(file_path: str, force: bool, dry_run: bool):
    """
    NOTE: This is an internal command and not meant to be used from outside.
    Stores a password in the given file path.

    As it could be security critical to pass a password as a command line parameter this method uses
    an environment variable instead.

    :param file_path:
    :param force: When set to true existing passwords will be overwritten. USE WITH CAUTION!
    :param dry_run: When set no passwords will actually be written and a preview of what WOULD be done will be printed.
    """

    SUMMARY_MANAGER.set_tmp_file(os.environ[SUMMARY_TMP_FILE_ENV_VARIABLE_NAME])

    final_secret_path = os.environ[SECRET_PATH_ENV_VARIABLE_NAME]

    username = os.environ[USERNAME_ENV_VARIABLE_NAME]
    password = os.environ[PASSWORD_ENV_VARIABLE_NAME]

    secret_content = _create_secret_content(username, password)

    # check if the file is empty
    file_stats = os.stat(file_path)
    if file_stats.st_size is not 0:
        # check if existing content matches the one we are about to write
        with open(file_path, 'r') as file:
            existing_content = file.read()
            if existing_content == secret_content:
                echo("Non-empty secret with identical content ignored: %s" % final_secret_path, info=True)
                return

        if not force:
            echo("Non-empty file with unequal content will NOT be overwritten: %s" % final_secret_path, warn=True)
            return
        else:
            echo("Non-empty file with unequal content WILL BE overwritten: %s" % final_secret_path, warn=True)

    if dry_run:
        # just print what would be executed
        secret_content = _create_secret_content(username, password, mask_pw=True)
        echo("%s:\n%s\n" % (final_secret_path, secret_content), info=True)
        SUMMARY_MANAGER.add_info("Would import: %s" % final_secret_path)
        return
    else:
        with open(file_path, 'w') as file:
            file.write(secret_content)
        SUMMARY_MANAGER.add_info("Imported %s" % final_secret_path)
        return


if __name__ == '__main__':
    cli()
