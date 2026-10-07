import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))


@pytest.fixture(scope="session")
def catalog():
    from evals.data import load_catalog
    return load_catalog()


@pytest.fixture(scope="session")
def qrels():
    from evals.data import load_qrels
    return load_qrels()
