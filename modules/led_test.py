import modules.mock_pigpio
import modules.mock_time
from modules.led import RGBLED
import pytest

def test_init():
    led = RGBLED(24, 23, 18)
    assert led.red == 24
    assert led.green == 23
    assert led.blue == 18
    assert led.pi is not None
    assert led.pi.setmode_called == 3

def test_get_color_pin():
    led = RGBLED(1,2,3)
    assert led.get_color_pin('red') == 1
    assert led.get_color_pin('green') == 2
    assert led.get_color_pin('blue') == 3

    with pytest.raises(ValueError) as ex:
        led.get_color_pin('fail')
    assert "is not valid" in str(ex.value)


def test_led():
    led = RGBLED(1, 2, 3)
    led.led('red', 100)
    assert led.pi.pulse == 255
    led.led('red', 0)
    assert led.pi.pulse == 0
    led.led('red', 50)
    assert led.pi.pulse == 127.5

    with pytest.raises(ValueError) as ex:
        led.led('red', 101)
    assert "is not in range" in str(ex.value)

    with pytest.raises(ValueError) as ex:
        led.led('red', -1)
    assert "is not in range" in str(ex.value)

def test_breathe():
    led = RGBLED(1, 2, 3)
    led.breathe('red')
    assert led.pi.pulse == 0
    assert led.pi.max_pulse == 255

    # this should not even run
    led = RGBLED(1, 2, 3)
    led.breathe('red', -1)
    assert led.pi.pulse == 0
    assert led.pi.max_pulse == 0

    # this should not even run
    led = RGBLED(1, 2, 3)
    with pytest.raises(ValueError) as ex:
        led.breathe('red', 101)

    led = RGBLED(1, 2, 3)
    led.breathe('red', 100)
    assert led.pi.pulse == 0
    assert led.pi.max_pulse == 255

