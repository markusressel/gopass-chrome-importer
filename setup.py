import subprocess

from setuptools import setup, find_packages

VERSION_NUMBER = "1.0.1"

GIT_BRANCH = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"])
GIT_BRANCH = GIT_BRANCH.decode()  # convert to standard string
GIT_BRANCH = GIT_BRANCH.rstrip()  # remove unnecessary whitespace

if GIT_BRANCH == "master":
    DEVELOPMENT_STATUS = "Development Status :: 5 - Production/Stable"
    VERSION_NAME = VERSION_NUMBER
elif GIT_BRANCH == "beta":
    DEVELOPMENT_STATUS = "Development Status :: 4 - Beta"
    VERSION_NAME = "%s-beta" % VERSION_NUMBER
elif GIT_BRANCH == "dev":
    DEVELOPMENT_STATUS = "Development Status :: 3 - Alpha"
    VERSION_NAME = "%s-dev" % VERSION_NUMBER
else:
    print("Unknown git branch, using pre-alpha as default")
    DEVELOPMENT_STATUS = "Development Status :: 2 - Pre-Alpha"
    VERSION_NAME = "%s-%s" % (VERSION_NUMBER, GIT_BRANCH)


def readme_type() -> str:
    import os
    if os.path.exists("README.rst"):
        return "text/x-rst"
    if os.path.exists("README.md"):
        return "text/markdown"


def readme() -> [str]:
    import os
    if os.path.exists("README.rst"):
        file_name = 'README.rst'
    elif os.path.exists("README.md"):
        file_name = 'README.md'
    else:
        return []

    with open(file_name) as f:
        return f.read()


def install_requirements() -> [str]:
    return read_requirements_file("requirements.txt")


def test_requirements() -> [str]:
    return read_requirements_file("test_requirements.txt")


def read_requirements_file(file_name: str):
    with open(file_name, encoding='utf-8') as f:
        requirements_file = f.readlines()
    return [r.strip() for r in requirements_file]


setup(
    name='gopass-chrome-importer',
    version=VERSION_NAME,
    description='A simple tool to import Chrome passwords into gopass.',
    long_description=readme(),
    long_description_content_type=readme_type(),
    license='MIT',
    author='Markus Ressel',
    author_email='mail@markusressel.de',
    url='https://github.com/markusressel/gopass-chrome-importer',
    packages=find_packages(),
    classifiers=[
        DEVELOPMENT_STATUS,
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    install_requires=install_requirements(),
    tests_require=test_requirements(),
    entry_points={
        'console_scripts': [
            'gopass-chrome-importer=gopass_chrome_importer.gopass_chrome_importer:cli'
        ]
    }
)
