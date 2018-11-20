def is_running_on_ci() -> bool:
    """
    :return: true when the current host is a CI, false otherwise
    """

    import os
    return os.getenv('CI', False) and os.getenv('TRAVIS', False)
