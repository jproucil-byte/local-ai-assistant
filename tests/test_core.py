import unittest
from local_ai_assistant.ollama_client import local_endpoint
from local_ai_assistant.config import Settings

class CoreTests(unittest.TestCase):
    def test_local_endpoint(self):
        self.assertEqual(local_endpoint('http://127.0.0.1:11434/'), 'http://127.0.0.1:11434')
        self.assertEqual(local_endpoint('http://localhost:11434'), 'http://localhost:11434')
    def test_remote_rejected(self):
        for value in ('https://localhost:11434', 'http://example.com',
                      'http://192.168.1.10:11434', 'http://localhost:11434/evil'):
            with self.assertRaises(ValueError):
                local_endpoint(value)
    def test_default_settings(self):
        self.assertTrue(Settings().model)

if __name__ == '__main__':
    unittest.main()
