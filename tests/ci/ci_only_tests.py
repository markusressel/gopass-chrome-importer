import unittest

from click.testing import CliRunner

from gopass_chrome_importer.gopass_chrome_importer import cli
from tests import DUMMY_FILE_PATH
from tests.ci import is_running_on_ci


class CiOnlyTests(unittest.TestCase):

    def test_real_run(self):
        """
        A real gopass import run with the test file
        """
        if not is_running_on_ci():
            print("Not running on CI, ignoring CI test.")
            return

        runner = CliRunner(echo_stdin=True)
        prog_name = runner.get_default_prog_name(cli)
        args = ['import', '-p', DUMMY_FILE_PATH, "-y"]
        cli.main(args=args or (), prog_name=prog_name, standalone_mode=False)


if __name__ == '__main__':
    unittest.main()
