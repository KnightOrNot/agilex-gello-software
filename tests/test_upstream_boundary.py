"""Keep local behavior out of the pinned upstream source."""

from pathlib import Path

import numpy as np
import pytest

from agilex_gello_software.robots.dynamixel import DynamixelRobot
from agilex_gello_software.upstream import verify_checkout
from gello.dynamixel import driver as upstream_driver
from gello.robots.dynamixel import DynamixelRobot as UpstreamRobot


def test_pinned_upstream_tree_is_unchanged():
    assert verify_checkout(Path(__file__).resolve().parents[1]) == []


@pytest.mark.parametrize("reference", [None, np.zeros(7)])
def test_calibration_multiturn_gripper_and_filter_match_upstream(
    monkeypatch, reference
):
    original_fake = upstream_driver.FakeDynamixelDriver
    raw = np.array([7, -8, 0.4, 1.2, -2, 4, np.deg2rad(180)])

    def create_fake(ids):
        driver = original_fake(ids)
        driver._joint_angles = raw.copy()
        return driver

    monkeypatch.setattr(upstream_driver, "FakeDynamixelDriver", create_fake)
    args = dict(
        joint_ids=(1, 2, 3, 4, 5, 6),
        joint_offsets=[np.pi] * 6,
        joint_signs=(1, -1, -1, -1, 1, 1),
        gripper_config=(7, 159, 201),
        start_joints=reference,
    )
    original, adapted = UpstreamRobot(**args), DynamixelRobot(**args)
    np.testing.assert_allclose(adapted.get_joint_state(), original.get_joint_state())
    for robot in (original, adapted):
        robot._driver._joint_angles += 0.1
    np.testing.assert_allclose(adapted.get_joint_state(), original.get_joint_state())
    adapted.close()


def test_local_driver_does_not_replace_upstream_classes():
    from agilex_gello_software.agents.gello_agent import GelloAgent
    from agilex_gello_software.dynamixel.driver import DynamixelDriver
    from gello.agents.gello_agent import GelloAgent as UpstreamAgent

    assert GelloAgent.act is UpstreamAgent.act
    assert not hasattr(UpstreamAgent, "close")
    assert upstream_driver.DynamixelDriver is not DynamixelDriver
