import modules.mock_RPi
import modules.mock_subprocess
from modules.idle import Idle
import pytest


def test_init():
    idle = Idle(3, 20)
    assert idle.timer != None
    assert idle.pin == 3
    assert idle.timeout == 20
    assert not idle.timer.is_alive()


def test_rising():
    idle = Idle(3, 20)
    idle.detect_motion()
    assert not idle.timer.is_alive()


def test_falling():
    idle = Idle(0, 20) # mock event just returns pin number, so 0 = falling (no motion detected)
    idle.detect_motion()
    assert idle.timer.is_alive()


def test_shutdown():
    idle = Idle(3, 20)
    assert idle.shutdown()
