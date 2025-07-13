# External Dependencies

The project relies on several external packages and services:

- **SQLite**: used for local data persistence. Databases are stored in the `databases/` folder.
- **psutil**: required for performance monitoring scripts.
- **Flask** and related packages: used by the optional web dashboard in `web_gui/`.
- **tqdm** and **rich**: provide progress bars and colored console output.
- **scikit-learn**: required for ML tests and analytics.
- **qiskit** and **qiskit-aer**: quantum simulation libraries used in tests.
- **qiskit-machine-learning**: enables QNN benchmarking and clustering tests.

Install the core dependencies using:

```bash
# Install core dependencies
pip install -r requirements.txt

# Optional extras are split into separate files so you can install only what you
# need:
pip install -r requirements-web.txt    # Web dashboard
pip install -r requirements-ml.txt     # Machine learning and analytics
```

For local testing or CI pipelines, use the provided `Makefile`:

```bash
make test
```

The `test` target installs the packages listed in `requirements-test.txt`
(including `requests`, `scikit-learn`, `qiskit`, `qiskit-aer`, and `qiskit-machine-learning`) before invoking `pytest`.

Some scripts expect certain JSON reports or configuration files to be present in
the working directory. Review the README files for details on each module.
