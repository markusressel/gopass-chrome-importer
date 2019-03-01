import os
import pickle

from click import echo
from click._unicodefun import click

from gopass_chrome_importer.summary import GopassImporterWarning, GopassImporterError


class SummaryManager:
    _infos = "infos"
    _warnings = "warnings"
    _errors = "errors"

    _default_summary_items: dict = {
        _infos: [],
        _warnings: [],
        _errors: []
    }

    summary_folder = "/dev/shm/gopass-chrome-importer/"
    summary_items_file_path: str = "/dev/shm/gopass-chrome-importer/summary"

    def read_from_filesystem(self) -> dict:
        """
        Reads the current summary from a file
        :return: the summary dict
        """
        if os.path.isfile(self.summary_items_file_path):
            with open(self.summary_items_file_path, 'rb') as summary_file:
                return pickle.load(summary_file)
        else:
            return self._default_summary_items

    def _write_to_filesystem(self, summary: dict) -> None:
        """
        Write the given summary to a file system
        :param summary: the summary dict to save
        """
        os.makedirs(self.summary_folder, exist_ok=True)
        with open(self.summary_items_file_path, 'wb') as summary_file:
            pickle.dump(summary, summary_file, protocol=pickle.HIGHEST_PROTOCOL)

    def clear(self):
        """
        Removes summary content of previous runs
        """
        for file in [self.summary_items_file_path]:
            if os.path.isfile(file):
                os.remove(file)

    def add_warning(self, secret_path: str, text: str) -> None:
        """
        Add a warning to the summary
        :param secret_path:
        :param text:
        """

        warning = GopassImporterWarning(secret_path, text)
        self._append_to_summary(warning)

    def add_error(self, secret_path: str, text: str) -> None:
        """
        Add an error to the summary
        :param secret_path:
        :param text:
        """
        error = GopassImporterError(secret_path, text)
        self._append_to_summary(error)

    def _append_to_summary(self, item: GopassImporterError or GopassImporterWarning or str) -> None:
        """
        Appends an item to the summary
        :param item:
        """
        summary = self.read_from_filesystem()

        if item is GopassImporterError:
            summary[self._warnings].append(item)
        elif item is GopassImporterWarning:
            summary[self._errors].append(item)
        else:
            summary[self._infos].append(str(item))

        self._write_to_filesystem(summary)

    def add_info(self, text):
        self._append_to_summary(text)

    def print_summary(self):
        summary = self.read_from_filesystem()
        infos = summary[self._infos]
        errors = summary[self._errors]
        warnings = summary[self._warnings]

        summary_title = "Summary"
        text = "%s\n" % summary_title + ('=' * len(summary_title)) + "\n"
        echo(click.style(text, fg='white'))

        text = ""
        for info in infos:
            text += str(info) + "\n"
        echo(text)

        text = ""
        for warning in warnings:
            text += str(warning) + "\n"
        echo(click.style(text, fg='yellow'))

        text = ""
        for error in errors:
            text += str(error) + "\n"
        echo(click.style(text, fg='red'), err=True)
