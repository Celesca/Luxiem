from lexiem.cli import STAGES


def test_stage_names():
    assert STAGES == ["collect", "extract", "normalize", "features", "model", "evaluate"]
