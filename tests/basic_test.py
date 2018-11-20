import os
import unittest

from click.testing import CliRunner

from gopass_chrome_importer.gopass_chrome_importer import cli


class TestBasicMethods(unittest.TestCase):
    def test_base_usage(self):
        """

        """
        runner = CliRunner()

        testfile = os.path.join(os.path.dirname(__file__), 'dummy_csv_file.csv')
        result = runner.invoke(cli, ['import', '-p', testfile, "-y"])

        self.assertEqual(result.exit_code, 0)

        # assert result.output == 'Hello Peter!\n'


if __name__ == '__main__':
    unittest.main()
