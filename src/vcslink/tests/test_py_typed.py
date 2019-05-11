from pathlib import Path


def test_py_typed():
    assert (Path(__file__).parents[1] / "py.typed").exists()
