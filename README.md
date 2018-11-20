# gopass-chrome-importer  [![Build Status](https://travis-ci.org/markusressel/gopass-chrome-importer.svg?branch=master)](https://travis-ci.org/markusressel/gopass-chrome-importer)
A simple tool to import Chrome passwords into [gopass](https://github.com/gopasspw/gopass).

# How it works

**gopass-chrome-importer** parses the `.csv` file that can be exported from chrome
and loops over each entry in the list which provides

* a **name** (of the entry)
* the **url**
* the **username**
* the **password**

## Determining the secret file path

1. Since not only passwords for websites are stored in chrome all entries are divided into categories 
which are later used as subfolders when creating the actual secrets in gopass. 
2. Next the url is simplified based on the category to provide a human readable name for the secret.
3. To improve usability with the gopass chrome and firefox plugin the username is used as the file name of the secret.

* `website`
  * the url is stripped down to only contain the domain (and all subdomains) f.ex. `import/website/smile.amazon.com/your@mail.com`
* `ip`
  * since saved passwords of IPs can be duplicates based on the network you are in
    these passwords are sorted into their own category and the url is stripped to only contain the IP (v4)
  * IPv6 is currently not detected and would be handled as a website
* `android`
  * the url is stripped down to only contain the package of the app f.ex. `import/android/com.paypal.android.p2pmobile/your@mail.com`

## Secret file content

The first line of a secret is always supposed to be a password 
with additional info added below separated by a `---` divider.
When a username is available it will be added to the additional info section
which can then be used by the chrome and firefox plugin:

```text
mypassword1234
---
user: myuser
```

If no user is available just the password is written to the file:

```text
mypassword1234
```

## Creating the secret

Since **gopass** does not provide a non-interactive way to create or modify secrets the fact that
secrets can not only be edited but also created using the `gopass edit` command is used to work around this
(security related) limitation. When executing `gopass edit /some/secret` **gopass** creates a temporary decrypted 
file inside `/dev/shm` for this secret which is then passed to `$EDITOR`. **gopass-chrome-importer** uses this to 
its advantage and writes itself into that env variable to process the temporarily decrypted file. 
First of all the existing file is checked to prevent overwriting of existing secret data. 
If those checks succeed the secret is written to the file in the form described above.
After that **gopass** encrypts the temporary file with the selected recipients and (if a remote is available) 
pushes it to the server. 


# Installing

Now that you hopefully have a good understanding of how this tool works lets actually try it out!

Since this package is not completely without dependencies it is recommended to install it inside a **virtualenv**:

```bash
python3 -m venv ~/path/to/new/virtual/environment
source ~/path/to/new/virtual/environment/bin/activate
pip3 install gopass-chrome-importer
```

# Usage

For basic usage the `import` command should be all you ever need.
**gopass-chrome-importer** has a couple of parameters to customize the import result
and you should take a look what they offer before actually importing anything.
For a quick overview call:

```bash
gopass-chrome-importer import --help
```

## Dry Run

To test things out before actually importing passwords into **gopass** (and possibly 
pushing them to origin) you can use the `-d` or `--dry-run` option. This will only output
secret paths and contents where passwords are masked as asterisks to give you an idea of what would 
happen.

An example output would look similar to this:
```text
Would import: /import/ip/127.0.0.1/joe
******
---
user: joe

Would import: /import/ip/192.168.0.1/admin
********************
---
user: admin
```

For safety **all** examples on this page will include this option. 


## Set the path to the chrome password export .csv

To set the path to the `export.csv` file just use the `-p` or `--path` option:

```bash
gopass-chrome-importer import --path "~/Downloads/Chrome Passwords.csv" --dry-run
```

## Changing the base import path

By default **gopass-chrome-importer** will import secrets into an `import/` folder. To change this simply
use the `-gb` or `--gopass-basepath` option:

```bash
gopass-chrome-importer import --path "~/Downloads/Chrome Passwords.csv" --gopass-basepath /test/ --dry-run
```

## --yes

By default **gopass** will ask you some questions when creating a secret like which recipients to use for this secret.
For large lists of passwords this can be quite a hassle. **gopass** has a built in `--yes` option to circumvent this 
by always using "Y" or the default (if *yes* is not an option). This parameter can also be used (in addition to `-y`)
in **gopass-chrome-importer** and will just pass it on to **gopass**.

```bash
gopass-chrome-importer import --path "~/Downloads/Chrome Passwords.csv" --gopass-basepath /test/ --yes --dry-run
```

## Overwrite existing passwords/file contents

When **gopass-chrome-importer** tries to save a password in a file that
already exists and that file is **not** empty it will (by default) **not change the file contents**
to prevent accidentally overwriting of existing passwords.

You can force **gopass-chrome-importer** to ignore this check by using the `-f` or `--force` option.

Although your existing passwords are backed up in a git and (hopefully) synced to a 
server side backend **be careful and think twice before using this option.**

```bash
gopass-chrome-importer import --path "~/Downloads/Chrome Passwords.csv" --gopass-basepath /test/ --yes --force --dry-run
```

# Contributing

GitHub is for social coding: if you want to write code, I encourage contributions through pull requests from forks
of this repository. Create GitHub tickets for bugs and new features and comment on the ones that you are interested in.


# License

```
MIT License

Copyright (c) 2018 Markus Ressel

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
