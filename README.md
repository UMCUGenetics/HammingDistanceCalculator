# python_template

![test](https://github.com/UMCUGenetics/python_template/actions/workflows/test.yml/badge.svg)
![lint](https://github.com/UMCUGenetics/python_template/actions/workflows/lint.yml/badge.svg)

Python template project - This repository can be used as a starting point / guide on how to setup a python repository, including automated tests and code formatting.

## GitHub repository creation

- Repository name: `Modules should have short, all-lowercase names. Underscores can be used in the module name if it improves readability. Python packages should also have short, all-lowercase names, although the use of underscores is discouraged.`
- Add README
- Add .gitignore: `python`
- Add License: `MIT`

Make sure to perform the following actions, after creating a new github repo:

- Create a develop branch.
- Configure branch protection rules.

## UV

UV supports packaged and unpackaged applications, this repository show cases a packaged application initiated with the command: `uv init --package .`. To create a simpler unpackaged application use: `uv init .`. Unpackaged applications can be used for single file scripts/tools, while packaged applications are used for (larger) tools requiring multiple files, distribution (pip) and tests separation.

Setup uv package and development dependencies:

```sh
uv init --package .
uv add --dev ruff
uv add --dev pytest
```

Run pytest and the python-template tool:

```sh
uv run pytest tests
uv run python-template World
uv run python-template --help
```

## GitHub Actions

This template project contains two GitHub actions workflows (`.github/workflos/`): `lint.yml` and `test.yml`. The lint workflow uses the [ruff-action](https://github.com/astral-sh/ruff-action) action to run ruff. The test workflow uses the [setup-uv action](https://github.com/astral-sh/setup-uv) to setup uv, install dependencies and run tests. Both actions are configured to run on each pull request and push to main and develop.

## pre-commit

Git pre-commit hooks enable you to run certain commands before each commit and can be used to check code style before committing. The file `.pre-commit-config.yaml` contains the [Ruff](https://docs.astral.sh/ruff/) [pre-commit](https://pre-commit.com) hook, which will automatically run Ruff before each commit. Run the following command to install the git commit hook: `pre-commit install`.
