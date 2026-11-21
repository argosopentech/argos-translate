# Developers

Use the repository's default branch as the base for pull requests. Install the
checkout in a virtual environment with `python -m pip install -e .`.

## Running unit tests

Install `pytest` and `pytest-socket`, then run the same model-free tests as CI:

```sh
ARGOS_CHUNK_TYPE=NONE python -m pytest --disable-socket -v \
  tests/test_package.py tests/test_tokenizer.py tests/test_translate.py
```

CI uses Ubuntu and Python 3.11. Dependency installation needs internet access;
the tests block sockets and use local fixtures and mocked translations. Keep the
explicit file list: `test_english_translations.py` requires installed models, and
`integration-tests/` contains separate manual scripts. Add new model-free test
files to `.github/workflows/python-package.yml` as needed.

## Formatting

Install `black` and `isort`, then run:

```sh
./scripts/format.sh
```

## Documentation

Keep changes focused on the affected pages. `docs/source/examples.rst` supplies
the homepage's Python example; keep the README example consistent with it.
`docs/source/settings.rst` is the maintained settings reference.

```sh
python -m pip install -r docs/requirements.txt
python -m sphinx -W --keep-going -b html docs docs/_build/html
python -m sphinx -W --keep-going -b linkcheck docs docs/_build/linkcheck
python -m pytest --disable-socket -q tests/test_docs.py
```

The HTML build and example check run on pull requests. External link checks run
on manual workflow dispatch because availability and rate limits vary. Review
`docs/_build/html/index.html` after changing markup. Example checks use mocks;
check real model output separately using the offline preparation guide.

Read the Docs uses `.readthedocs.yml`. After merging, verify that the `latest`
build points to the intended branch and commit in the Read the Docs dashboard;
repository changes alone cannot configure its webhook or version settings.
