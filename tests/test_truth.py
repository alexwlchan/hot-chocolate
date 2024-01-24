from hotchocolate import __version__


def test_version() -> None:
    assert __version__ == "2024.1"


def test_truth() -> None:
    assert True
