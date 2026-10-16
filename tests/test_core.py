import unittest
from io import BytesIO
import json
from unittest.mock import patch
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

    def test_thinking_option_only_sent_for_qwen35(self):
        from local_ai_assistant.ollama_client import chat
        for model, thinking, expected in (('qwen3.5:4b', False, False),
                                          ('qwen3.5:9b', True, True),
                                          ('gemma3:4b', True, None)):
            with self.subTest(model=model, thinking=thinking), patch(
                    'local_ai_assistant.ollama_client.urllib.request.urlopen',
                    return_value=BytesIO(b'{"message":{"content":"OK"}}')) as request:
                self.assertEqual(chat('http://127.0.0.1:11434', model,
                                      [{'role': 'user', 'content': 'Hello'}],
                                      extended_thinking=thinking), 'OK')
                payload = json.loads(request.call_args.args[0].data)
                if expected is None:
                    self.assertNotIn('think', payload)
                else:
                    self.assertIs(payload['think'], expected)

if __name__ == '__main__':
    unittest.main()
