import json
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import config
import llm_chat_completion


class TestAx650ChatCompletion(unittest.TestCase):
    def _write_conversation(self, messages):
        temp = tempfile.NamedTemporaryFile("w", delete=False, suffix=".json", encoding="utf-8")
        try:
            json.dump(messages, temp)
            temp.flush()
            return temp.name
        finally:
            temp.close()

    def test_dispatcher_selects_ax650_branch(self):
        conversation_file = self._write_conversation([])
        original_llm = config.LLM
        try:
            config.LLM = "ax650"
            with patch("llm_chat_completion.chat_completion_ax650", return_value="ok") as mocked:
                result = llm_chat_completion.llm_chat_completion(conversation_file)
                self.assertEqual(result, "ok")
                mocked.assert_called_once_with(conversation_file)
        finally:
            config.LLM = original_llm
            os.unlink(conversation_file)

    def test_ax650_request_uses_latest_user_prompt_only(self):
        conversation_file = self._write_conversation([
            {"role": "system", "content": "persona"},
            {"role": "user", "content": "first question"},
            {"role": "assistant", "content": "answer"},
            {"role": "user", "content": "latest question"},
        ])

        response_mock = MagicMock()
        response_mock.json.return_value = {"response": "latest answer"}
        response_mock.raise_for_status.return_value = None

        with patch("llm_chat_completion.requests.post", return_value=response_mock) as mocked_post:
            result = llm_chat_completion.chat_completion_ax650(conversation_file)

        self.assertEqual(result, "latest answer")
        _, kwargs = mocked_post.call_args
        payload = kwargs["json"]
        self.assertEqual(payload["prompt"], "latest question")
        self.assertNotIn("messages", payload)
        os.unlink(conversation_file)

    def test_ax650_parser_uses_response_field(self):
        conversation_file = self._write_conversation([
            {"role": "user", "content": "what now"},
        ])

        response_mock = MagicMock()
        response_mock.json.return_value = {
            "response": "from response field",
            "message": {"content": "from message field"},
        }
        response_mock.raise_for_status.return_value = None

        with patch("llm_chat_completion.requests.post", return_value=response_mock):
            result = llm_chat_completion.chat_completion_ax650(conversation_file)

        self.assertEqual(result, "from response field")
        os.unlink(conversation_file)

    def test_ax650_network_failure_returns_fallback(self):
        conversation_file = self._write_conversation([
            {"role": "user", "content": "hello"},
        ])

        with patch("llm_chat_completion.requests.post", side_effect=Exception("network down")):
            result = llm_chat_completion.chat_completion_ax650(conversation_file)

        self.assertEqual(result, llm_chat_completion.AX650_FALLBACK_RESPONSE)
        os.unlink(conversation_file)

    def test_ax650_missing_response_field_returns_fallback(self):
        conversation_file = self._write_conversation([
            {"role": "user", "content": "hello"},
        ])

        response_mock = MagicMock()
        response_mock.json.return_value = {"message": {"content": "not used"}}
        response_mock.raise_for_status.return_value = None

        with patch("llm_chat_completion.requests.post", return_value=response_mock):
            result = llm_chat_completion.chat_completion_ax650(conversation_file)

        self.assertEqual(result, llm_chat_completion.AX650_FALLBACK_RESPONSE)
        os.unlink(conversation_file)

    def test_ax650_reset_calls_stop_then_reset_with_system_prompt(self):
        call_order = []

        get_response = MagicMock()
        get_response.raise_for_status.return_value = None

        post_response = MagicMock()
        post_response.raise_for_status.return_value = None

        def get_side_effect(*args, **kwargs):
            call_order.append("stop")
            return get_response

        def post_side_effect(*args, **kwargs):
            call_order.append("reset")
            return post_response

        with patch("llm_chat_completion.requests.get", side_effect=get_side_effect) as mocked_get, patch(
            "llm_chat_completion.requests.post", side_effect=post_side_effect
        ) as mocked_post:
            result = llm_chat_completion.ax650_soft_reset_and_reassert_prompt()

        self.assertTrue(result)
        self.assertEqual(call_order, ["stop", "reset"])
        mocked_get.assert_called_once()
        mocked_post.assert_called_once()

        stop_url = mocked_get.call_args.args[0]
        reset_url = mocked_post.call_args.args[0]
        reset_payload = mocked_post.call_args.kwargs["json"]

        self.assertEqual(stop_url, getattr(config, "AX650_RUNTIME_STOP_ENDPOINT", "http://127.0.0.1:8000/api/stop"))
        self.assertEqual(reset_url, getattr(config, "AX650_RUNTIME_RESET_ENDPOINT", "http://127.0.0.1:8000/api/reset"))
        self.assertEqual(reset_payload["system_prompt"], config.SYSTEM_MESSAGE_TEXT)


if __name__ == "__main__":
    unittest.main()
