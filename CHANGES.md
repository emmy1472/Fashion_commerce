# Changelog

## Unreleased

- messaging: Add async WebSocket tests, fallback communicator (asgiref) to enable running websocket tests without daphne, and use in-memory channel layer during tests to avoid requiring Redis locally. (tests pass locally)
- messaging: Improve consumers, serializers, views, and tests; add CI workflow and `requirements-dev.txt`.
