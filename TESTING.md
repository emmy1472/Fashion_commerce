# Testing & Development Notes ✅

This file documents how to run the test suite (including WebSocket tests) locally and how to enable developer dependencies.

## Install dev dependencies

Install the dev requirements (recommended) to enable `daphne` and more test tooling:

PowerShell:

```
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process; .\env1\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

Or on cmd.exe:

```
.\env1\Scripts\activate.bat
pip install -r requirements-dev.txt
```

## Run tests

Run the Django test suite for the messaging app:

```
python socialcom\manage.py test messaging -v 2
```

To run just the async websocket tests:

```
python socialcom\manage.py test messaging.tests_async -v 2
```

### Notes
- The test suite uses an in-memory Channels layer during `manage.py test` runs so Redis is not required locally.
- A fallback WebSocket communicator using `asgiref.testing.ApplicationCommunicator` is provided so tests can run even without `daphne`; installing `daphne` is recommended when possible because it provides a more realistic test environment.
- If you see SQLite locking issues, ensure dev requirements are installed or run tests individually; tests are written to avoid common locking by using `TransactionTestCase` and `database_sync_to_async` where necessary.

If anything fails, copy the test output here and I'll debug it for you.
