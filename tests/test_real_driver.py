"""Physical initialization must never continue with synthetic joint feedback."""

import pytest

from agilex_gello_software.dynamixel import driver
from agilex_gello_software.robots.dynamixel import DynamixelRobot


def test_real_robot_disables_fake_fallback(monkeypatch):
    def fail(ids, **kwargs):
        assert kwargs["use_fake_fallback"] is False
        raise RuntimeError("physical feedback unavailable")

    monkeypatch.setattr(driver, "DynamixelDriver", fail)
    with pytest.raises(RuntimeError, match="physical feedback"):
        DynamixelRobot([1, 2], real=True)


def test_failed_torque_setup_releases_port(monkeypatch):
    class Driver:
        closed = False

        def __init__(self, *args, **kwargs):
            pass

        def set_torque_mode(self, enabled):
            raise RuntimeError("torque setup failed")

        def close(self):
            Driver.closed = True

    monkeypatch.setattr(driver, "DynamixelDriver", Driver)
    with pytest.raises(RuntimeError, match="torque setup"):
        DynamixelRobot([1, 2], real=True)
    assert Driver.closed


def test_explicit_simulation_remains_available():
    robot = DynamixelRobot([1, 2], real=False)
    try:
        assert robot.get_joint_state().tolist() == [0, 0]
    finally:
        robot.close()
