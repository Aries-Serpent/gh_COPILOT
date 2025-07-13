# Qiskit 1.0+ Environment Validation

This guide explains how to clean up old Qiskit installations when `pip list` shows multiple versions. Mixed versions (e.g., `qiskit 0.39` alongside `qiskit 1.x`) can cause inconsistent behavior.

## Remove Old Packages
1. Uninstall all Qiskit packages:
   ```bash
   pip uninstall -y qiskit qiskit-terra qiskit-aer qiskit-ibm-provider qiskit-ibm-runtime
   ```
2. Check your `site-packages` directory and delete any leftover `qiskit*` folders.

## Reinstall Qiskit >= 1.0
1. Reinstall the required dependencies using the repository's test requirements:
   ```bash
   pip install -r requirements-test.txt
   ```
   This installs `qiskit>=1.4,<2.0` and compatible extras like `qiskit-aer`.
2. Verify the version:
   ```bash
   python -c "import qiskit; print(qiskit.__qiskit_version__)"
   ```

## Validate the Environment
Run the full test suite to confirm everything works with the clean installation:
```bash
make test
```

If you previously installed Qiskit via conda or your system package manager, remove those packages as well before reinstalling.
