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

## Environment variable
The MYTHME_DIR environment variable points to a directory where mythme
stores saved queries and other items. It's also where you can create a mythme.yaml
file to [configure](#configuration) mythme.
```
export MYTHME_DIR="~/.mythme"
```
(default is `~/.mythme`)

## Configuration
In many cases no configuration is required. This is especially true if you're
running mythme on MythTV's master backend host.
### Database
For [Database Configuration](https://www.mythtv.org/wiki/Config.xml#Database),
mythme looks for `~/.mythtv/config.xml` and uses the `<Database>` element if present.
### MythTV API server
To determine the [MythTV Services API](https://www.mythtv.org/wiki/Services_API) host, mythme tries
`BackendServerAddr` and `BackendStatusPort` from MythTV's `settings` db table.
### Custom config
Settings specified in `$MYTHME_DIR/mythme.yaml` override the autoconfig values above.
Here's an example mythme.yaml:
```yaml
database:
  host: '192.168.0.70'
  port: 3306
  database: mythconverg
  username: mythtv
  password: mythtv

mythtv_api_base: http://192.168.0.70:6544
```

## Run server
Make sure `~/.local/bin` is in your $PATH.
```
mythme
```

## Command line options
```
-h, --help   show this help message
--version    show mythme's version
--host HOST  Server host
--port PORT  Server port
```

## Channel icons
Channel icons are disabled by default.
To enable, click the dropdown caret next to the Channel column heading.
Check the "Icons" box and confirm.