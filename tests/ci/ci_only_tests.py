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

        runner = CliRunner()
        result = runner.invoke(cli, ['import', '-p', DUMMY_FILE_PATH, "-y"])

        self.assertEqual(result.exit_code, 0)


if __name__ == '__main__':
    unittest.main()
