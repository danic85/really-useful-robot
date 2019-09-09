from modules.config import Config
import pytest

def test_init():
    cfg = Config()
    assert cfg.get('LEDR') == 13


def test_get():
    cfg = Config()
    assert cfg.get('LEDR', False) == '13'
    with pytest.raises(KeyError) as ex:
        cfg.get('TEST')