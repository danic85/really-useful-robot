import modules.mock_pigpio
from modules.servo import Servo
import pytest

def test_init():
    # Pin 1, default values
    sv = Servo(1)
    assert sv.pos == 20000
    assert sv.min == 25
    assert sv.max == 40000
    assert sv.pin == 1

    assert sv.pi is not None
    assert sv.pi.setmode_called == 1

    # Override defaults
    sv = Servo(10, 20, 30, 40)
    assert sv.pos == 20
    assert sv.min == 30
    assert sv.max == 40
    assert sv.pin == 10

def test_get_pos():
    sv = Servo(1)
    assert sv.get_pos() == 20000

def test_move():
    sv = Servo(1, 50, 0, 200)
    # test absolute values
    sv.move(10)
    assert sv.pos == 20
    sv.move(20)
    assert sv.pos == 40
    sv.move(50)
    assert sv.pos == 100

    # test relative values
    sv.move(5, True)
    assert sv.pos == 110
    sv.move(-10, True)
    assert sv.pos == 90

    # test that relative value changes do not affect absolute values
    sv.move(20)
    assert sv.pos == 40

    # test boundary values
    sv.move(0)
    assert sv.pos == 0
    sv.move(100)
    assert sv.pos == 200

    # test out of range values
    with pytest.raises(ValueError) as ex:
        sv.move(-10)
    assert "out of range" in str(ex.value)
    with pytest.raises(ValueError) as ex:
        sv.move(101)
    assert "out of range" in str(ex.value)




