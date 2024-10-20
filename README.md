# mythme
**Find and record programs on MythTV**

<img alt="mythme" src="https://raw.githubusercontent.com/donaldoakes/mythme/main/docs/img/mm-light.png#gh-light-mode-only" width="50px" />
<img alt="mythme" src="https://raw.githubusercontent.com/donaldoakes/mythme/main/docs/img/mm-dark.png#gh-dark-mode-only" width="50px" />

Inspired by [MythWeb](https://github.com/MythTV/mythweb)'s Canned Searches feature, mythme makes it easy
to create and save custom queries. For example, a query named `Horror Movies of the 1930s`:
<picture>
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/donaldoakes/mythme/main/docs/img/query-light.png">
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/donaldoakes/mythme/main/docs/img/query-dark.png">
  <img alt="mythme query" src="https://raw.githubusercontent.com/donaldoakes/mythme/main/docs/img/query-light.png">
</picture>

The result after clicking Save:
![mythme programs](https://raw.githubusercontent.com/donaldoakes/mythme/main/docs/img/programs-light.png#gh-light-mode-only)
![mythme programs](https://raw.githubusercontent.com/donaldoakes/mythme/main/docs/img/programs-dark.png#gh-dark-mode-only)


## Prerequisites
- python 3
- mariadb connector/c

## Environment variable
```
MYTHME_DIR="~/.mythme"
```
(default is '~/.mythme')

## Installation
```
python -m pip install mythme
```

## Run server
```
mythme
```
