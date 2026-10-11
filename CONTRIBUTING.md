# Contributing

Pull requests welcome. Keep each PR focused on one logical change. Small
is better than big.

## Development setup

```
git clone https://github.com/inormis/spanlint
cd spanlint
pip install -e ".[dev]"
```

## Running the checks

Before pushing, run:

```
ruff check .
ruff format --check .
mypy
pytest
```

CI runs the same four commands on Python 3.11 and 3.12.

## Commit style

Short, verb-led subject lines under 72 characters. No Conventional
Commits prefixes (`feat:`, `fix:`, etc.). Write the message as you would
type it in a hurry: `Added gen_ai.response.id rule`, `Fix typo in README`.

## Tests

Every behavior ships with a test in the same commit.
