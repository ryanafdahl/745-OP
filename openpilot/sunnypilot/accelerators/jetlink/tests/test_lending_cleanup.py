"""Regression tests for descriptor ownership when a Jetlink lease cannot open.

These tests never touch the USB gadget, device params, or vehicle interfaces.
"""
import unittest
from pathlib import Path
from unittest import mock

from openpilot.sunnypilot.accelerators.jetlink import lending


class TestFailedBorrowCleanup(unittest.TestCase):
  def test_failed_connect_closes_the_socket(self):
    conn = mock.Mock()
    conn.connect.side_effect = FileNotFoundError('no owner listening')
    with mock.patch.object(lending.socket, 'socket', return_value=conn):
      self.assertIsNone(lending.borrow(path=Path('/unused/jetlink-test')))
    conn.close.assert_called_once_with()

  def test_failed_settimeout_closes_the_socket(self):
    conn = mock.Mock()
    conn.settimeout.side_effect = OSError('socket unavailable')
    with mock.patch.object(lending.socket, 'socket', return_value=conn):
      self.assertIsNone(lending.borrow(path=Path('/unused/jetlink-test')))
    conn.close.assert_called_once_with()

  def test_creation_failure_returns_none(self):
    with mock.patch.object(lending.socket, 'socket', side_effect=OSError('no descriptors')):
      self.assertIsNone(lending.borrow(path=Path('/unused/jetlink-test')))

  def test_close_error_does_not_hide_connection_failure(self):
    conn = mock.Mock()
    conn.connect.side_effect = ConnectionRefusedError('no owner')
    conn.close.side_effect = OSError('already closed')
    with mock.patch.object(lending.socket, 'socket', return_value=conn):
      self.assertIsNone(lending.borrow(path=Path('/unused/jetlink-test')))
    conn.close.assert_called_once_with()


class TestFailedListenerCleanup(unittest.TestCase):
  def test_failed_bind_closes_the_socket(self):
    self._assert_failure_closes('bind')

  def test_failed_listen_closes_the_socket(self):
    self._assert_failure_closes('listen')

  def test_failed_settimeout_closes_the_socket(self):
    self._assert_failure_closes('settimeout')

  def _assert_failure_closes(self, operation):
    sock = mock.Mock()
    getattr(sock, operation).side_effect = OSError('listener unavailable')
    lender = lending.Lender(lambda: True, lambda: True, path=Path('/unused/jetlink-test'))
    with (mock.patch.object(lender, '_clear_stale'),
          mock.patch.object(lending.socket, 'socket', return_value=sock),
          mock.patch.object(lending.gadget.log, 'exception')):
      self.assertFalse(lender.start())
    self.assertFalse(lender.listening)
    self.assertIsNone(lender._thread)
    sock.close.assert_called_once_with()

  def test_creation_failure_returns_false(self):
    lender = lending.Lender(lambda: True, lambda: True, path=Path('/unused/jetlink-test'))
    with (mock.patch.object(lender, '_clear_stale'),
          mock.patch.object(lending.socket, 'socket', side_effect=OSError('no descriptors')),
          mock.patch.object(lending.gadget.log, 'exception')):
      self.assertFalse(lender.start())
    self.assertFalse(lender.listening)


if __name__ == '__main__':
  unittest.main()
