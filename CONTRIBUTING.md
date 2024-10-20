## Initial dev setup
```
git clone https://github.com/donaldoakes/mythme.git
cd mythme
python -m venv .venv
. .venv/bin/activate
brew install mariadb-connector-c
pip install -r requirements-dev.txt
```

## VS Code
  - Install the recommended extensions (.vscode/extensions.json)
  - Open the Command Pallet (ctrl-shift-p), and type "Python: Select Interpreter"
  - Select the venv created in [Dev Setup](#dev-setup)

## Env setup
Create a local .env with information for MariaDB connection. Use .env.sample as a guide.

## Type checks
```
mypy .
```

## Build [mythme-ui](https://github.com/donaldoakes/mythme-ui)
```
cd ..
git clone https://github.com/donaldoakes/mythme-ui.git
cd mythme-ui
npm run build
npm run deliver
```

## FastAPI
Start the uvicorn server:
```
cd src
uvicorn api.main:app --app-dir=src --reload
```

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

## Increment version
 - pyproject.toml
 - src/mythme/__init__.py

## Build wheel:
`python -m build`
