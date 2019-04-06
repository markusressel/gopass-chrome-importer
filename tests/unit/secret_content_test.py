from gopass_chrome_importer import gopass_chrome_importer
from tests import CliTestBase


class SecretContentTests(CliTestBase):
    """
    Unit tests
    """

    def test_creation(self):
        username = "username"
        password = "password"

        expected = "{}\n---\nuser: {}".format(password, username)

        content = gopass_chrome_importer._create_secret_content(
            username=username,
            password=password,
            mask_pw=False)

        self.assertEqual(content, expected)

    def test_without_user(self):
        password = "password"

        expected = password

        content = gopass_chrome_importer._create_secret_content(
            password=password,
            mask_pw=False)

        self.assertEqual(content, expected)

    def test_masked(self):
        username = "username"
        password = "password"

        expected = "{}\n---\nuser: {}".format('*' * 10, username)

        content = gopass_chrome_importer._create_secret_content(
            username=username,
            password=password,
            mask_pw=True)

        self.assertEqual(content, expected)
