# External Dependencies

The project relies on several external packages and services:

- **SQLite**: used for local data persistence. Databases are stored in the `databases/` folder.
- **psutil**: required for performance monitoring scripts.
- **Flask** and related packages: used by the optional web dashboard in `web_gui/`.
- **tqdm** and **rich**: provide progress bars and colored console output.

Install Python dependencies using:

```bash
pip install -r requirements.txt
```

For local testing or CI pipelines, use the provided `Makefile`:

```bash
make test
```

The `test` target installs the packages listed in `requirements-test.txt`
(including `requests`) before invoking `pytest`.

Some scripts expect certain JSON reports or configuration files to be present in
the working directory. Review the README files for details on each module.
