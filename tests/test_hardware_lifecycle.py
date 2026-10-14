"""The real driver must fail explicitly and release failed initializations."""

from unittest.mock import Mock

import numpy as np
import pytest

from agilex_gello_software.dynamixel import driver
from agilex_gello_software.robots.dynamixel import DynamixelRobot


def test_real_driver_disables_fake_fallback(monkeypatch):
    hardware = Mock()
    factory = Mock(return_value=hardware)
    monkeypatch.setattr(driver, "DynamixelDriver", factory)
    robot = DynamixelRobot(joint_ids=(1, 2), real=True)
    assert factory.call_args.kwargs["use_fake_fallback"] is False
    robot.close()
    hardware.close.assert_called_once()


@pytest.mark.parametrize("failure", ["torque", "alignment"])
def test_constructor_failure_closes_driver(monkeypatch, failure):
    hardware = Mock()
    if failure == "torque":
        hardware.set_torque_mode.side_effect = RuntimeError("hardware failed")
    else:
        hardware.get_joints.side_effect = RuntimeError("hardware failed")
    monkeypatch.setattr(driver, "DynamixelDriver", Mock(return_value=hardware))
    with pytest.raises(RuntimeError, match="hardware failed"):
        DynamixelRobot(joint_ids=(1, 2), real=True, start_joints=np.zeros(2))
    hardware.close.assert_called_once()
