import unittest

from gopass_chrome_importer import gopass_chrome_importer
from tests import DUMMY_FILE_PATH, CliTestBase, only_cli


class IntegrationTests(CliTestBase):

    def test_dry_run(self):
        """
        A simple dry run with the test file
        """

        self._run_cli_cmd(args=['import', '-p', DUMMY_FILE_PATH, "-y", "--dry-run"])

    @only_cli
    def test_real_run(self):
        """
        A real gopass import run with the test file
        """
        secrets = gopass_chrome_importer._read_csv(DUMMY_FILE_PATH)

        self._run_cli_cmd(args=['import', '-p', DUMMY_FILE_PATH, "-y"])


if __name__ == '__main__':
    unittest.main()
