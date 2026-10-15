"""Exercise real transport threading with fake SDK packet/port objects."""

from types import SimpleNamespace
from unittest.mock import Mock

import numpy as np
import pytest

from agilex_gello_software.dynamixel import driver as module


@pytest.fixture
def transport(monkeypatch):
    port = Mock()
    port.openPort.return_value = True
    port.setBaudRate.return_value = True
    packet = Mock()
    packet.write1ByteTxRx.return_value = (module.upstream.COMM_SUCCESS, 0)
    group = Mock()
    group.addParam.return_value = True
    group.txRxPacket.return_value = module.upstream.COMM_SUCCESS
    group.isAvailable.return_value = True

    def value(motor_id, address, length):
        if address == module.upstream.ADDR_PRESENT_POSITION:
            return (-2048 if motor_id == 1 else 1024) & 0xFFFFFFFF
        return (-60 if motor_id == 1 else 30) & 0xFFFFFFFF

    group.getData.side_effect = value
    monkeypatch.setattr(module.DynamixelDriver, "_prepare_port", lambda self: None)
    monkeypatch.setattr(module.upstream, "PortHandler", Mock(return_value=port))
    monkeypatch.setattr(module.upstream, "PacketHandler", Mock(return_value=packet))
    monkeypatch.setattr(module.upstream, "GroupSyncRead", Mock(return_value=group))
    monkeypatch.setattr(module.upstream, "GroupSyncWrite", Mock())
    drivers = []

    def create():
        result = module.DynamixelDriver((1, 2), max_retries=1)
        drivers.append(result)
        return result

    yield SimpleNamespace(port=port, packet=packet, group=group, create=create)
    for driver in drivers:
        driver.close()


def test_signed_feedback_units_and_idempotent_close(transport):
    driver = transport.create()
    positions, velocities = driver.get_positions_and_velocities()
    np.testing.assert_allclose(positions, [-np.pi, np.pi / 2])
    np.testing.assert_allclose(velocities, np.array([-60, 30]) * 0.229 * 2 * np.pi / 60)
    driver.close()
    driver.close()
    assert not driver._reading_thread.is_alive()
    transport.port.closePort.assert_called_once()
    with pytest.raises(RuntimeError, match="closed"):
        driver.get_joints()


@pytest.mark.parametrize("field", ["open", "baudrate", "torque"])
def test_partial_initialization_closes_port(transport, field):
    if field == "open":
        transport.port.openPort.return_value = False
    elif field == "baudrate":
        transport.port.setBaudRate.return_value = False
    else:
        transport.packet.write1ByteTxRx.return_value = (-3001, 0)
    with pytest.raises(RuntimeError, match="Cannot initialize"):
        transport.create()
    assert transport.port.closePort.called


def test_continuous_packet_failures_reject_cached_state(transport):
    driver = transport.create()
    driver.get_joints()
    transport.group.txRxPacket.return_value = -3001
    driver._reading_thread.join(timeout=1)
    with pytest.raises(RuntimeError, match="failed 10 times"):
        driver.get_joints()


def test_missing_packet_field_is_reported(transport):
    transport.group.isAvailable.return_value = False
    driver = transport.create()
    with pytest.raises(RuntimeError, match="Incomplete"):
        driver.get_positions_and_velocities()


def test_stale_feedback_is_not_returned(transport):
    driver = transport.create()
    driver.get_joints()
    driver._stop_thread.set()
    driver._reading_thread.join(timeout=1)
    driver._last_successful_read -= 2
    with pytest.raises(RuntimeError, match="stale"):
        driver.get_positions_and_velocities()


def test_first_read_deadline_does_not_wait_for_serial_lock(transport):
    transport.group.txRxPacket.return_value = -3001
    driver = transport.create()
    with driver._lock:
        with pytest.raises(RuntimeError, match="Timed out"):
            driver._snapshot(timeout_s=0.03)


def test_real_adapter_refuses_fake_fallback():
    with pytest.raises(ValueError, match="FakeDynamixelDriver"):
        module.DynamixelDriver((1,), use_fake_fallback=True)


def test_failed_open_without_serial_handle_preserves_initial_error(transport):
    transport.port.ser = None
    transport.port.openPort.return_value = False
    with pytest.raises(RuntimeError, match="Failed to open the port"):
        transport.create()
    transport.port.closePort.assert_not_called()


def test_busy_port_never_kills_processes_or_changes_permissions(monkeypatch):
    monkeypatch.setattr(module.os.path, "exists", lambda path: True)
    monkeypatch.setattr(module.os, "access", lambda path, mode: True)
    monkeypatch.setattr(module.shutil, "which", lambda name: "/usr/bin/lsof")
    calls = []

    def run(args, **kwargs):
        calls.append(args)
        assert args == ["lsof", "/dev/test-gello"]
        assert kwargs["timeout"] == 1.0
        return SimpleNamespace(returncode=0, stdout="COMMAND PID\nreader 123\n")

    monkeypatch.setattr(module.subprocess, "run", run)
    with pytest.raises(RuntimeError, match="port is busy"):
        module.DynamixelDriver((1,), port="/dev/test-gello", max_retries=1)
    assert len(calls) == 1


def test_initialization_interrupt_closes_port(transport):
    transport.packet.write1ByteTxRx.side_effect = KeyboardInterrupt
    with pytest.raises(KeyboardInterrupt):
        transport.create()
    assert transport.port.closePort.called
