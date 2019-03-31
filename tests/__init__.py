import os
import unittest

from click.testing import CliRunner

from gopass_chrome_importer.gopass_chrome_importer import cli

DUMMY_FILE_PATH = testfile = os.path.join(os.path.dirname(__file__), 'dummy_csv_file.csv')


def is_running_on_ci() -> bool:
    """
    :return: true when the current host is a CI, false otherwise
    """

    import os
    return os.getenv('CI', False) and os.getenv('TRAVIS', False)


def only_cli(item_to_decorate: object or classmethod):
    """
    Decorator to run a test only on CI.
    This decorator can be applied to a class or class method
    :param item_to_decorate: the class or method to decorate
    :return: the decorated class or method
    """

    def decorate_method(method):
        if not is_running_on_ci():
            print("Not running on CI, ignoring CI test: {}".format(method.__name__))
            return

        return method

    def decorate_class(cls):
        for attr in cls.__dict__:  # there's probably a better way to do this
            if callable(getattr(cls, attr)):
                setattr(cls, attr, decorate_method(getattr(cls, attr)))
        return cls

    if callable(item_to_decorate):
        return decorate_method(item_to_decorate)
    elif isinstance(item_to_decorate, object):
        return decorate_class(item_to_decorate)
    else:
        raise AttributeError("Unsupported type: {}".format(item_to_decorate))


class CliTestBase(unittest.TestCase):
    """
    Base class for testing click cli commands
    """

    def _run_cli_cmd(self, prog_name: str = None, args: list = None) -> any:
        """
        Runs a cli command and returns it's output

        :param prog_name: name of the command to execute (?!)
        :param args: command arguments as a list
        :return:
        """
        runner = CliRunner(echo_stdin=True)
        if not prog_name:
            prog_name = runner.get_default_prog_name(cli)

        return cli.main(args=args or (), prog_name=prog_name, standalone_mode=False)


if __name__ == '__main__':
    unittest.main()
