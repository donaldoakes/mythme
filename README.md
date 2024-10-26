# mythme
**Find and record programs on MythTV**

Inspired by [MythWeb](https://github.com/MythTV/mythweb)'s Canned Searches feature, mythme makes it easy
to create and save custom queries. For example, a query named `Horror Movies of the 1930s`:

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/donaldoakes/mythme/main/docs/img/query-dark.png">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/donaldoakes/mythme/main/docs/img/query-light.png">
  <img alt="mythme query" src="https://raw.githubusercontent.com/donaldoakes/mythme/main/docs/img/query-light.png">
</picture>

The result after clicking Save:

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/donaldoakes/mythme/main/docs/img/programs-dark.png">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/donaldoakes/mythme/main/docs/img/programs-light.png">
  <img alt="mythme programs" src="https://raw.githubusercontent.com/donaldoakes/mythme/main/docs/img/programs-light.png">
</picture>


## Prerequisites
- python 3
- mariadb connector/c

## Installation
This installs to a local virtual environment.
```
python -m venv ~/.local --system-site-packages
~/.local/bin/pip install mythme
```

## Environment variables
Be sure ~/.local/bin is in your $PATH.
```
MYTHME_DIR="~/.mythme"
```
(default is '~/.mythme')

## Configuration


## Run server
```
mythme
```

## Channel icons
Channel icons are disabled by default.
To enable, click the dropdown caret next to the Channel column heading.
Check the "Icons" box and confirm.