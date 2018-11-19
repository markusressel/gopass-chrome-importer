#!/usr/bin/env python3

import click
import subprocess
import re


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


@click.group()
def cli():
    pass


@cli.command(name="import")
@click.option('-path', '-p', required=True, type=str, help='Path to the chrome password export .csv file.')
@click.option('-gopass-subpath', '-gp', required=False, type=str, default="websites/",
              help='The path in gopass where all entries are imported to.')
@click.option('-step', '-s', required=False, type=bool,
              help='Set to true to step through each csv file entry manually.')
def c_import(path: str, gopass_subpath: str, step: bool):
    """Imports all items in the chrome password export"""

    entries = _read_csv(path)

    for entry in entries:
        if entry["name"]:
            site = entry["name"].replace('www.', '')
        else:
            site = entry["url"].replace('https://www.', '').replace('www.', '')

        if entry["username"]:
            user = entry["username"]
        else:
            # TODO: generate username that will never collide with an existing one
            rolling_counter_for_website = 0
            user = "site_pw_%s" % rolling_counter_for_website

        secret_path = "%s%s/%s" % (gopass_subpath, site, user)
        click.echo(secret_path)

        run_shell_command("gopass insert %s" % (secret_path))

    click.echo("Done.")


if __name__ == '__main__':
    cli()
