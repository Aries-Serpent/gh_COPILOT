# Archive Scripts and Flake8

The `archive/` directory, including all its subdirectories, contains historical scripts preserved for reference.
These files are no longer maintained and generate numerous flake8 errors.
To keep linting focused on active code, the `archive/` directory and all its subdirectories are excluded in `.flake8` rather than refactoring all archived scripts.

With the move to **Ruff** for linting, the exclusion policy remains the same. Each Ruff run records a `lint_sessions` entry in `analytics.db`, preserving a history of every automated correction session.
