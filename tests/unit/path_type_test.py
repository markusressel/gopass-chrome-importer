from gopass_chrome_importer import gopass_chrome_importer
from gopass_chrome_importer.gopass_chrome_importer import UrlType
from tests import CliTestBase


class PathTypeTests(CliTestBase):
    """
    Unit tests
    """

    def test_ip(self):
        url = "http://127.0.0.1/login.wft"
        self._assertType(url, UrlType.IP)

    def test_ip_with_port(self):
        url = "http://127.0.0.1:1234"
        self._assertType(url, UrlType.IP)

    def test_ip_with_port_and_path(self):
        url = "http://127.0.0.1:1234/login.wft"
        self._assertType(url, UrlType.IP)

    def test_domain(self):
        url = "https://www.google.de"
        self._assertType(url, UrlType.DOMAIN)

    def test_domain_with_port_and_path(self):
        url = "https://www.google.de:234/sdsa"
        self._assertType(url, UrlType.DOMAIN)

    def test_android(self):
        url = "android://biubOBhziubziubIUbhiul56757KJjkjklJI787tnhoihjpoit638790798GBzugigbuGViu_fdsjk78hgHgu-JH6K9NB==@com.paypal.android.p2pmobile/"
        self._assertType(url, UrlType.ANDROID)

    def _assertType(self, url: str, expected: UrlType):
        """
        Helper method to compare the _find_type() method result with an expected type.
        :param url: the url to use
        :param expected: the expected result type
        """
        result = gopass_chrome_importer._find_type(url)
        self.assertEqual(result, expected)
