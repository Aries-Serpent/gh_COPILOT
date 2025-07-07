# Contributor Guidelines

This repository follows a few common conventions to help keep development consistent.

## Development Requirements
- **Python**: version 3.8 or higher is required.
- Install core dependencies with `pip install -r requirements.txt`.
- Optional extras are available in the `requirements-*.txt` files and may be installed as needed.

## Running Tests
- Tests rely on the `GH_COPILOT_WORKSPACE` environment variable. Set it to your workspace path if it is not already defined.
- Run tests with `make test`. You can also execute `pytest` directly once dependencies are installed.

## Formatting and Linting
- Format code with `autopep8` and sort imports with `isort`.
- Lint the project using `flake8`.

## Commit Messages
- Use short, imperative commit messages (e.g., "Add support for new API") to keep history clear.

## Project Notes
- Keep documentation up to date with these limitations so users do not expect unsupported functionality.
- References to quantum optimization or other advanced capabilities in the documentation describe future goals. These features are **not implemented**.
- Do **not** modify any bundled SQLite databases under version control (see the `databases/` folder).
- Additional guidelines and DUAL COPILOT compliance requirements can be found in the `documentation/` directory.

