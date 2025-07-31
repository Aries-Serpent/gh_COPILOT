# Archive Scripts and Flake8

The `archive/` directory, including all its subdirectories, contains historical scripts preserved for reference.
These files are no longer maintained and generate numerous flake8 errors.
To keep linting focused on active code, the `archive/` directory and all its subdirectories are excluded in `.flake8` rather than refactoring all archived scripts.
