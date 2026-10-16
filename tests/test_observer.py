import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Event
import time
import unittest
from unittest.mock import patch

from PySide6.QtWidgets import QApplication, QDialog
from local_ai_assistant.config import Settings
from local_ai_assistant.main import SettingsDialog, Window


class ObserverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.app.setQuitOnLastWindowClosed(False)

    def setUp(self):
        self.settings_patch = patch('local_ai_assistant.main.Settings.load', return_value=Settings())
        self.settings_patch.start()
        self.capture_patch = patch('local_ai_assistant.main.capture_primary_screen', return_value=b'frame')
        self.capture = self.capture_patch.start()
        self.chat_patch = patch('local_ai_assistant.main.chat', return_value='Visible screen summary')
        self.chat = self.chat_patch.start()
        self.window = Window()

    def tearDown(self):
        self.window.stop_watch()
        self.wait_for(lambda: self.window.thread is None)
        self.window.close()
        self.app.processEvents()
        self.chat_patch.stop()
        self.capture_patch.stop()
        self.settings_patch.stop()

    def wait_for(self, condition):
        deadline = time.monotonic() + 5
        while not condition() and time.monotonic() < deadline:
            self.app.processEvents()
            time.sleep(0.005)
        self.assertTrue(condition(), 'Qt worker did not finish in time')

    def test_watch_requires_start_and_does_not_fill_chat_history(self):
        self.assertFalse(self.window.watching)
        self.assertFalse(self.window.watch_timer.isActive())
        self.capture.assert_not_called()
        self.window.watch_button.click()
        self.wait_for(lambda: self.window.thread is None)
        self.assertEqual(self.window.observation.toPlainText(), 'Visible screen summary')
        self.assertEqual(len(self.window.messages), 1)
        self.assertTrue(self.window.watch_timer.isActive())
        self.assertEqual(self.window.watch_timer.interval(), 15000)
        self.assertEqual(self.chat.call_args.args[3], b'frame')
        self.window.watch_button.click()
        self.assertFalse(self.window.watch_timer.isActive())
        self.window.observe_screen()
        self.assertEqual(self.capture.call_count, 1)

    def test_stop_discards_inflight_result_and_prevents_overlapping_work(self):
        release = Event()
        started = Event()

        def slow_chat(*args):
            started.set()
            release.wait(3)
            return 'Old result'

        self.chat.side_effect = slow_chat
        self.window.toggle_watch()
        try:
            self.wait_for(started.is_set)
            self.window.observe_screen()
            self.assertEqual(self.capture.call_count, 1)
            self.window.stop_watch()
            self.window.toggle_watch()  # Restart must not accept a previous session's result.
        finally:
            release.set()
        self.wait_for(lambda: self.window.thread is None)
        self.assertEqual(self.window.observation.toPlainText(), '')
        self.assertTrue(self.window.watch_timer.isActive())

    def test_capture_failure_stops_watch(self):
        self.capture.side_effect = RuntimeError('No display')
        self.window.toggle_watch()
        self.assertFalse(self.window.watching)
        self.assertIn('No display', self.window.watch_status.text())
        self.chat.assert_not_called()

    def test_stop_during_analysis_discards_result_without_rescheduling(self):
        release = Event()
        self.chat.side_effect = lambda *args: (release.wait(3) and 'Late result')
        self.window.toggle_watch()
        self.window.stop_watch()
        release.set()
        self.wait_for(lambda: self.window.thread is None)
        self.assertEqual(self.window.observation.toPlainText(), '')
        self.assertFalse(self.window.watch_timer.isActive())
        self.assertIn('No automatic captures', self.window.watch_status.text())

    def test_model_failure_stops_watch(self):
        self.chat.side_effect = RuntimeError('Model does not support images')
        self.window.toggle_watch()
        self.wait_for(lambda: self.window.thread is None)
        self.assertFalse(self.window.watching)
        self.assertIn('Model does not support images', self.window.watch_status.text())
        self.assertEqual(len(self.window.messages), 1)

    def test_chat_while_watching_uses_fresh_frame_and_resumes_watch(self):
        self.window.toggle_watch()
        self.wait_for(lambda: self.window.thread is None)
        self.capture.return_value = b'fresh-frame'
        self.window.input.setPlainText('What is this error?')
        self.window.send()
        self.wait_for(lambda: self.window.thread is None)
        self.assertEqual(self.chat.call_args.args[3], b'fresh-frame')
        self.assertEqual(self.window.messages[-1]['role'], 'assistant')
        self.assertTrue(self.window.watch_timer.isActive())
        self.window.clear_chat()
        self.assertFalse(self.window.watching)
        self.assertEqual(self.window.observation.toPlainText(), '')

    def test_close_stops_watch(self):
        self.window.toggle_watch()
        self.wait_for(lambda: self.window.thread is None)
        self.window.close()
        self.assertFalse(self.window.watching)
        self.assertFalse(self.window.watch_timer.isActive())

    def test_opacity_preview_cancel_and_save(self):
        dialog = SettingsDialog(self.window.settings, self.window)
        dialog.opacity.setValue(55)
        self.assertAlmostEqual(self.window.windowOpacity(), .55, delta=.01)
        with patch('local_ai_assistant.main.SettingsDialog', return_value=dialog), \
                patch.object(dialog, 'exec', return_value=QDialog.DialogCode.Rejected):
            self.window.open_settings()
        self.assertEqual(self.window.windowOpacity(), 1)
        dialog.opacity.setValue(65)
        dialog.interval.setValue(30)
        with patch('local_ai_assistant.main.SettingsDialog', return_value=dialog), \
                patch.object(dialog, 'exec', return_value=QDialog.DialogCode.Accepted), \
                patch.object(self.window.settings, 'save') as save:
            self.window.open_settings()
        save.assert_called_once()
        self.assertEqual(self.window.settings.opacity, 65)
        self.assertEqual(self.window.settings.watch_interval, 30)
        self.assertAlmostEqual(self.window.windowOpacity(), .65, delta=.01)
        dialog.close()


class ObserverSettingsTests(unittest.TestCase):
    def test_old_settings_and_new_settings_roundtrip(self):
        with TemporaryDirectory() as tmp, patch('local_ai_assistant.config.config_path', return_value=Path(tmp) / 'settings.json'):
            path = Path(tmp) / 'settings.json'
            path.write_text(json.dumps({'model': 'gemma3:4b'}), encoding='utf-8')
            self.assertEqual(Settings.load().opacity, 100)
            self.assertEqual(Settings.load().watch_interval, 15)
            Settings(opacity=60, watch_interval=20).save()
            self.assertEqual(Settings.load().opacity, 60)
            self.assertEqual(Settings.load().watch_interval, 20)

    def test_settings_bounds(self):
        self.assertEqual(Settings(opacity=0).opacity, 30)
        self.assertEqual(Settings(watch_interval=0).watch_interval, 5)
        self.assertEqual(Settings(opacity='bad').opacity, 100)
        self.assertEqual(Settings(watch_interval=None).watch_interval, 15)


if __name__ == '__main__':
    unittest.main()
