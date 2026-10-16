# Organization Demo

A small Python package for creating and listing organizations in an in-memory directory. It is intentionally minimal so future changes—such as duplicate-name validation, renaming, and deactivation—can be developed against an existing codebase and test suite.

## Requirements

- Python 3.10 or newer
- pytest to run the tests

## Run the tests

Install the project and its test dependency, then run pytest:

```powershell
python -m pip install -e ".[test]"
python -m pytest
```

## Usage

```python
from organization_demo import OrganizationDirectory

directory = OrganizationDirectory()
directory.create_organization("Northwind")
print(directory.list_organizations())
```

Organizations are kept in memory for the lifetime of the directory instance and are listed in creation order.
