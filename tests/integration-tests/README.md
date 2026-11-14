# Integration tests

These scripts require installed translation models and are not part of the
model-free unit-test suite. From the repository root, install English-to-Spanish
and prepare sentence-splitting resources while connected, then run:

```sh
python tests/integration-tests/memoryleak.py
```

The script performs 100,000 translations for manual memory observation; it is
not a quick pass/fail test. See [Developers.md](../../Developers.md) for unit tests
and the [offline guide](../../docs/source/troubleshooting.rst) before disconnecting.
