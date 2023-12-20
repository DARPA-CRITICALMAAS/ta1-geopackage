from pytest import fixture


@fixture
def test_dir(tmp_path):
    yield tmp_path / ".test"
