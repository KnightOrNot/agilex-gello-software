"""Device lifecycle adapter; calibration and filtering reuse upstream methods."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from gello.robots.dynamixel import DynamixelRobot as UpstreamDynamixelRobot


class DynamixelRobot(UpstreamDynamixelRobot):
    def __init__(
        self,
        joint_ids: Sequence[int],
        joint_offsets: Sequence[float] | None = None,
        joint_signs: Sequence[int] | None = None,
        real: bool = False,
        port: str = "/dev/ttyUSB0",
        baudrate: int = 57600,
        gripper_config: tuple[int, float, float] | None = None,
        start_joints: np.ndarray | None = None,
    ) -> None:
        from agilex_gello_software.dynamixel.driver import DynamixelDriver

        # Initialize upstream calibration with a harmless fake transport, then
        # inject our real transport. No upstream globals or classes are patched.
        super().__init__(
            joint_ids,
            joint_offsets=joint_offsets,
            joint_signs=joint_signs,
            real=False,
            port=port,
            gripper_config=gripper_config,
        )
        self._joint_offsets = np.asarray(self._joint_offsets, dtype=np.float64)
        if real:
            self._driver = DynamixelDriver(
                self._joint_ids, port=port, baudrate=baudrate, use_fake_fallback=False
            )
        try:
            self._driver.set_torque_mode(False)
            if start_joints is not None:
                reference = np.asarray(start_joints, dtype=np.float64)
                current = self.get_joint_state()
                if reference.shape != current.shape or not np.all(
                    np.isfinite(reference)
                ):
                    raise ValueError(
                        "start_joints must match finite GELLO state dimensions"
                    )
                arm_count = len(self._joint_ids) - int(gripper_config is not None)
                self._joint_offsets[:arm_count] += (
                    2
                    * np.pi
                    * np.round(
                        (current[:arm_count] - reference[:arm_count]) / (2 * np.pi)
                    )
                    * self._joint_signs[:arm_count]
                )
        except BaseException:
            self._driver.close()
            raise

    def close(self) -> None:
        self._driver.close()
