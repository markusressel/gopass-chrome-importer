import unittest

from click.testing import CliRunner

from gopass_chrome_importer.gopass_chrome_importer import cli
from tests import DUMMY_FILE_PATH


class TestBasicMethods(unittest.TestCase):

    def test_dry_run(self):
        """
        A simple dry run with the test file
        """
        runner = CliRunner(echo_stdin=True)
        prog_name = runner.get_default_prog_name(cli)
        args = ['import', '-p', DUMMY_FILE_PATH, "-y", "--dry-run"]
        cli.main(args=args or (), prog_name=prog_name, standalone_mode=False)


if __name__ == '__main__':
    unittest.main()
