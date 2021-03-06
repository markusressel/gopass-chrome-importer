"""
Module for managing summary entries
"""

import os
import pickle
import random
import shutil
import string

import click


class SummaryManager:
    """
    Class used to manage summary entries
    """

    _infos = "infos"
    _warnings = "warnings"
    _errors = "errors"

    _default_summary_items = {
        _infos: [],
        _warnings: [],
        _errors: []
    }

    tmp_file_path = ""

    def __init__(self, tmp_file_path: str or None = None):
        """
        Constructor
        :param tmp_file_path: the tmp file to store the summary or None if no such file exists yet
        """
        self.set_tmp_file(tmp_file_path)

    def set_tmp_file(self, tmp_file_path: str or None = None) -> None:
        """
        Set the path of the temp file used to store the summary entries
        :param tmp_file_path: path to the temp file
        """
        if tmp_file_path:
            self.tmp_file_path = tmp_file_path
        else:
            tmp_dir = self._select_tmp_file_path()
            if not tmp_dir:
                raise ValueError("No valid directory for tmp file found")
            random_file_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(25))
            self.tmp_file_path = os.path.join(tmp_dir,
                                              "gopass-chrome-importer",
                                              "summary_%s" % random_file_name)

    @staticmethod
    def _select_tmp_file_path() -> str or None:
        """
        :return: a possible path to store a temporary file in or None if no valid temp path could be found
        """

        # try to use memory mnt first
        for path in ["/dev/shm", "/tmp"]:
            if os.path.isdir(path):
                return path

        return None

    def get_tmp_file_path(self) -> str:
        """
        :return: the path of the temp file used to store the summary while processing
        """
        return self.tmp_file_path

    def read_from_filesystem(self) -> dict:
        """
        Reads the current summary from a file
        :return: the summary dict
        """
        if os.path.isfile(self.tmp_file_path):
            with open(self.tmp_file_path, 'rb') as summary_file:
                return pickle.load(summary_file)
        else:
            return self._default_summary_items

    def _write_to_filesystem(self, summary: dict) -> None:
        """
        Write the given summary to a file system
        :param summary: the summary dict to save
        """
        os.makedirs(os.path.dirname(self.tmp_file_path), exist_ok=True)
        with open(self.tmp_file_path, 'wb') as summary_file:
            pickle.dump(summary, summary_file, protocol=pickle.HIGHEST_PROTOCOL)

    def clear(self):
        """
        Removes temp files of previous runs
        """
        shutil.rmtree(os.path.dirname(self.tmp_file_path), ignore_errors=True)

    def add_info(self, text: any) -> None:
        """
        Add an info message to the summary
        :param text: the text to add
        """
        self._append_to_summary(text)

    def add_warning(self, text: any) -> None:
        """
        Add a warning to the summary
        :param text: warning message
        """
        self._append_to_summary(text, warn=True)

    def add_error(self, text: any) -> None:
        """
        Add an error to the summary
        :param text: error message
        """
        self._append_to_summary(text, error=True)

    def _append_to_summary(self, item: any, warn: bool = False, error: bool = False) -> None:
        """
        Appends an item to the summary
        :param item:
        """
        summary = self.read_from_filesystem()

        text = str(item)
        if error:
            summary[self._errors].append(text)
        elif warn:
            summary[self._warnings].append(text)
        else:
            summary[self._infos].append(text)

        self._write_to_filesystem(summary)

    def print_summary(self):
        """
        Prints the current state of the summary to the console
        """
        summary = self.read_from_filesystem()
        infos = summary[self._infos]
        errors = summary[self._errors]
        warnings = summary[self._warnings]

        summary_title = "Summary (%s warning(s), %s error(s))" % (len(warnings), len(errors))
        text = "%s\n" % summary_title + ('=' * len(summary_title)) + "\n"
        click.echo(click.style(text, fg='white'))

        text = ""
        for info in infos:
            text += str(info) + "\n"
        click.echo(click.style(text, fg='green'))

        text = ""
        for warning in warnings:
            text += str(warning) + "\n"
        click.echo(click.style(text, fg='yellow'))

        text = ""
        for error in errors:
            text += str(error) + "\n"
        click.echo(click.style(text, fg='red'), err=True)
