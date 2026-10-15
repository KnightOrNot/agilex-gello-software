"""Explicit calibration and close support over the original GELLO agent."""

from __future__ import annotations

import os
from dataclasses import dataclass

import numpy as np

from agilex_gello_software.robots.dynamixel import DynamixelRobot
from gello.agents.gello_agent import PORT_CONFIG_MAP
from gello.agents.gello_agent import DynamixelRobotConfig as UpstreamRobotConfig
from gello.agents.gello_agent import GelloAgent as UpstreamGelloAgent

__all__ = ["PORT_CONFIG_MAP", "DynamixelRobotConfig", "GelloAgent"]


@dataclass
class DynamixelRobotConfig(UpstreamRobotConfig):
    gripper_config: tuple[int, float, float] | None = None

    def make_robot(
        self, port: str = "/dev/ttyUSB0", start_joints: np.ndarray | None = None
    ) -> DynamixelRobot:
        return DynamixelRobot(
            joint_ids=self.joint_ids,
            joint_offsets=self.joint_offsets,
            joint_signs=self.joint_signs,
            gripper_config=self.gripper_config,
            real=True,
            port=port,
            start_joints=start_joints,
        )


class GelloAgent(UpstreamGelloAgent):
    def __init__(
        self,
        port: str,
        dynamixel_config: UpstreamRobotConfig | None = None,
        start_joints: np.ndarray | None = None,
    ) -> None:
        if dynamixel_config is None:
            if not os.path.exists(port):
                raise FileNotFoundError(port)
            if port not in PORT_CONFIG_MAP:
                raise ValueError(f"Port {port} not in upstream config map")
            dynamixel_config = PORT_CONFIG_MAP[port]
        # Also adapt a config constructed by the original upstream API.
        config = DynamixelRobotConfig(
            joint_ids=dynamixel_config.joint_ids,
            joint_offsets=dynamixel_config.joint_offsets,
            joint_signs=dynamixel_config.joint_signs,
            gripper_config=dynamixel_config.gripper_config,
        )
        super().__init__(port=port, dynamixel_config=config, start_joints=start_joints)

    def close(self) -> None:
        self._robot.close()
