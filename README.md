# mythme
**Find and record programs on MythTV**

<img alt="mythme" src="docs/img/mm-light.png#gh-light-mode-only" width="50px" />
<img alt="mythme" src="docs/img/mm-dark.png#gh-dark-mode-only" width="50px" />

Inspired by [MythWeb](https://github.com/MythTV/mythweb)'s Canned Searches feature, mythme makes it easy
to create and save custom queries. For example, a query named `Horror Movies of the 1930s`:
![mythme query](https://raw.githubusercontent.com/donaldoakes/mythme/main/docs/img/query-light.png#gh-light-mode-only)
![mythme query](https://raw.githubusercontent.com/donaldoakes/mythme/main/docs/img/query-dark.png#gh-dark-mode-only)
The result after clicking Save:
![mythme programs](https://raw.githubusercontent.com/donaldoakes/mythme/main/docs/img/programs-light.png#gh-light-mode-only)
![mythme programs](https://raw.githubusercontent.com/donaldoakes/mythme/main/docs/img/programs-dark.png#gh-dark-mode-only)


## prerequisites
- python 3
- mariadb connector/c

## environment variable
```
MYTHME_DIR="~/.mythme"
```
(default is '~/.mythme')

## run uvicorn
```
uvicorn mythme.api.main:app --host=0.0.0.0 --port=8000 --app-dir=src
```

## run main
```
python src/mythme
```

## editable install
```
python -m pip install -e .
```