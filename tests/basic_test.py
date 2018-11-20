import unittest

from click.testing import CliRunner

from gopass_chrome_importer.gopass_chrome_importer import cli
from tests import DUMMY_FILE_PATH


class TestBasicMethods(unittest.TestCase):

    def test_dry_run(self):
        """
        A simple dry run with the test file
        """
        runner = CliRunner()
        result = runner.invoke(cli, ['import', '-p', DUMMY_FILE_PATH, "-y", "--dry-run"])

        self.assertEqual(result.exit_code, 0)


if __name__ == '__main__':
    unittest.main()
