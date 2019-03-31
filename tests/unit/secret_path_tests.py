import unittest

from gopass_chrome_importer import gopass_chrome_importer


class SecretPathTests(unittest.TestCase):
    """
    Unit tests
    """

    def test_website_with_name(self):
        base_path = "/"
        name = "Google"
        username = "user"
        url = "https://www.google.de"

        expected = "/website/{}/{}".format(name, username)

        path = gopass_chrome_importer._create_secret_path(
            base_path=base_path,
            name=name,
            username=username,
            url=url)

        self.assertEqual(path, expected)

    def test_website_without_name(self):
        base_path = "/"
        name = ""
        username = "user"
        url = "https://www.google.de"

        expected = "/website/google.de/{}".format(username)

        path = gopass_chrome_importer._create_secret_path(
            base_path=base_path,
            name=name,
            username=username,
            url=url)

        self.assertEqual(path, expected)

    def test_website_with_port(self):
        base_path = "/"
        name = ""
        username = "user"
        url = "https://www.google.de:12345"

        expected = "/website/google.de:12345/{}".format(username)

        path = gopass_chrome_importer._create_secret_path(
            base_path=base_path,
            name=name,
            username=username,
            url=url)

        self.assertEqual(path, expected)

    def test_website_with_port_equal_to_protocol(self):
        base_path = "/"
        name = ""
        username = "user"
        url = "http://www.google.de:80/login"

        expected = "/website/google.de/{}".format(username)

        path = gopass_chrome_importer._create_secret_path(
            base_path=base_path,
            name=name,
            username=username,
            url=url)

        self.assertEqual(path, expected)

        url = "https://www.google.de:443"
        path = gopass_chrome_importer._create_secret_path(
            base_path=base_path,
            name=name,
            username=username,
            url=url)

        self.assertEqual(path, expected)

    def test_android(self):
        base_path = "/"
        name = ""
        username = "user"
        url = "android://biubOBhziubziubIUbhiul56757KJjkjklJI787tnhoihjpoit638790798GBzugigbuGViu_fdsjk78hgHgu-JH6K9NB==@com.paypal.android.p2pmobile/"

        expected = "/android/com.paypal.android.p2pmobile/{}".format(username)

        path = gopass_chrome_importer._create_secret_path(
            base_path=base_path,
            name=name,
            username=username,
            url=url)

        self.assertEqual(path, expected)

    def test_ip(self):
        base_path = "/"
        name = ""
        username = "user"
        url = "http://127.0.0.1/bla/bli/blubbs"

        expected = "/ip/127.0.0.1/{}".format(username)

        path = gopass_chrome_importer._create_secret_path(
            base_path=base_path,
            name=name,
            username=username,
            url=url)

        self.assertEqual(path, expected)

    def test_ip_with_port(self):
        base_path = "/"
        name = ""
        username = "user"
        url = "http://127.0.0.1:8888/bla/bli/blubbs"

        expected = "/ip/127.0.0.1:8888/{}".format(username)

        path = gopass_chrome_importer._create_secret_path(
            base_path=base_path,
            name=name,
            username=username,
            url=url)

        self.assertEqual(path, expected)


if __name__ == '__main__':
    unittest.main()
