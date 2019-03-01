class GopassImporterError:
    secret_path: str
    error_text: str

    def __init__(self, secret_path: str, error_text: str):
        self.secret_path = secret_path
        self.error_text = error_text


class GopassImporterWarning:
    secret_path: str
    warning_text: str

    def __init__(self, secret_path: str, warning_text: str):
        self.secret_path = secret_path
        self.warning_text = warning_text
