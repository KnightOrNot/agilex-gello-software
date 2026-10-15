"""Bounded, real-device adapter over the unchanged upstream transport."""

from __future__ import annotations

import os
import shutil
import subprocess
import time
from collections.abc import Sequence
from threading import Event, Lock, current_thread

import numpy as np

from gello.dynamixel import driver as upstream

DynamixelDriverProtocol = upstream.DynamixelDriverProtocol
FakeDynamixelDriver = upstream.FakeDynamixelDriver


class DynamixelDriver(upstream.DynamixelDriver):
    """Reuse upstream commands; own initialization, feedback and cleanup policy.

    The upstream driver remains available as ``gello.dynamixel.driver``. This
    adapter never frees another process's port or silently substitutes fake data.
    """

    def __init__(
        self,
        ids: Sequence[int],
        servo_types: Sequence[str] | None = None,
        port: str = "/dev/ttyUSB0",
        baudrate: int = 57600,
        max_retries: int = 3,
        use_fake_fallback: bool = False,
    ) -> None:
        if use_fake_fallback:
            raise ValueError("Use FakeDynamixelDriver explicitly for simulation")
        if max_retries < 1:
            raise ValueError("max_retries must be positive")
        self._state_lock = Lock()
        self._read_ready = Event()
        self._read_error: Exception | None = None
        self._last_successful_read: float | None = None
        self._closed = False
        try:
            super().__init__(
                ids,
                servo_types=servo_types,
                port=port,
                baudrate=baudrate,
                max_retries=max_retries,
                use_fake_fallback=False,
            )
        except BaseException as exc:
            try:
                self.close()
            except Exception as cleanup_error:
                exc.add_note(f"Dynamixel cleanup also failed: {cleanup_error}")
            raise

    def _initialize_with_retries(self) -> bool:
        for attempt in range(self._max_retries):
            try:
                self._initialize_hardware()
                return True
            except Exception as exc:
                self._close_port()
                if attempt == self._max_retries - 1:
                    raise RuntimeError(
                        f"Cannot initialize Dynamixel on {self._port}: {exc}"
                    ) from exc
                self._stop_thread.wait(2.0)
        return False

    def _prepare_port(self) -> None:
        if not os.path.exists(self._port):
            raise FileNotFoundError(self._port)
        if not os.access(self._port, os.R_OK | os.W_OK):
            raise PermissionError(f"No read/write permission for {self._port}")
        if shutil.which("lsof"):
            result = subprocess.run(
                ["lsof", self._port],
                capture_output=True,
                text=True,
                timeout=1.0,
                check=False,
            )
            if result.returncode == 0 and len(result.stdout.splitlines()) > 1:
                raise RuntimeError(f"Dynamixel port is busy: {self._port}")

    def _initialize_hardware(self) -> None:
        # Upstream's constructor catches torque failures and may still start a
        # reader. Keep packet layout identical, but propagate that failure here.
        self._prepare_port()
        self._portHandler = upstream.PortHandler(self._port)
        self._packetHandler = upstream.PacketHandler(2.0)
        self._groupSyncRead = upstream.GroupSyncRead(
            self._portHandler,
            self._packetHandler,
            upstream.ADDR_PRESENT_VELOCITY,
            upstream.LEN_PRESENT_VELOCITY + upstream.LEN_PRESENT_POSITION,
        )
        self._groupSyncWrite = upstream.GroupSyncWrite(
            self._portHandler,
            self._packetHandler,
            upstream.ADDR_GOAL_POSITION,
            upstream.LEN_GOAL_POSITION,
        )
        self._groupSyncWriteCurrent = upstream.GroupSyncWrite(
            self._portHandler,
            self._packetHandler,
            upstream.ADDR_GOAL_CURRENT,
            upstream.LEN_GOAL_CURRENT,
        )
        if not self._portHandler.openPort():
            raise RuntimeError("Failed to open the port")
        if not self._portHandler.setBaudRate(self._baudrate):
            raise RuntimeError(f"Failed to set baudrate {self._baudrate}")
        for motor_id in self._ids:
            if not self._groupSyncRead.addParam(motor_id):
                raise RuntimeError(f"Failed to add motor ID {motor_id}")
        self.set_torque_mode(False)
        self._start_reading_thread()

    def _read_joint_states(self) -> None:
        failures = 0
        try:
            while not self._stop_thread.wait(0.01):
                with self._lock:
                    result = self._groupSyncRead.txRxPacket()
                    if result != upstream.COMM_SUCCESS:
                        failures += 1
                        if failures >= 10:
                            raise RuntimeError(
                                f"Dynamixel communication failed 10 times: {result}"
                            )
                        continue
                    values = []
                    for address, length in (
                        (upstream.ADDR_PRESENT_POSITION, upstream.LEN_PRESENT_POSITION),
                        (upstream.ADDR_PRESENT_VELOCITY, upstream.LEN_PRESENT_VELOCITY),
                    ):
                        sample = []
                        for motor_id in self._ids:
                            if not self._groupSyncRead.isAvailable(
                                motor_id, address, length
                            ):
                                raise RuntimeError(
                                    f"Incomplete Dynamixel feedback for ID {motor_id}"
                                )
                            value = self._groupSyncRead.getData(
                                motor_id, address, length
                            )
                            sample.append(
                                value - 0x100000000 if value > 0x7FFFFFFF else value
                            )
                        values.append(np.asarray(sample, dtype=np.int64))
                # Separate state/transport locks keep read deadlines effective
                # even while an SDK transaction is waiting on the serial port.
                with self._state_lock:
                    self._joint_angles, self._velocities = values
                    self._last_successful_read = time.monotonic()
                failures = 0
                self._read_ready.set()
        except Exception as exc:
            with self._state_lock:
                self._read_error = exc
            self._read_ready.set()

    def _snapshot(self, timeout_s: float = 3.0) -> tuple[np.ndarray, np.ndarray]:
        deadline = time.monotonic() + timeout_s
        while True:
            if self._closed:
                raise RuntimeError("Dynamixel driver is closed")
            with self._state_lock:
                if self._read_error is not None:
                    raise RuntimeError(str(self._read_error)) from self._read_error
                if self._last_successful_read is not None:
                    if time.monotonic() - self._last_successful_read > 1.0:
                        raise RuntimeError("Dynamixel feedback is stale (> 1 second)")
                    return self._joint_angles.copy(), self._velocities.copy()
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise RuntimeError("Timed out waiting for first Dynamixel feedback")
            self._read_ready.wait(min(remaining, 0.01))

    def get_joints(self) -> np.ndarray:
        positions, _ = self._snapshot()
        return positions / 2048.0 * np.pi

    def get_positions_and_velocities(self) -> tuple[np.ndarray, np.ndarray]:
        positions, velocities = self._snapshot()
        return positions / 2048.0 * np.pi, velocities * 0.229 * 2 * np.pi / 60

    def _close_port(self) -> None:
        port = getattr(self, "_portHandler", None)
        if port is not None and getattr(port, "ser", None) is not None:
            port.closePort()

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        stop = getattr(self, "_stop_thread", None)
        if stop is not None:
            stop.set()
        self._read_ready.set()
        reader = getattr(self, "_reading_thread", None)
        can_join = (
            reader is not None
            and reader.ident is not None
            and reader is not current_thread()
        )
        try:
            if can_join:
                reader.join(timeout=2.0)
        finally:
            self._close_port()
        if can_join and reader.is_alive():
            reader.join(timeout=1.0)
            if reader.is_alive():
                raise RuntimeError("Dynamixel reader did not stop after port close")
