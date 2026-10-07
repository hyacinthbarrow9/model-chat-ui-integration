import pathlib
import unittest

ROOT = pathlib.Path(__file__).parents[1]


class OpenWebUITests(unittest.TestCase):
    def test_readme_has_current_setup_boundary(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        for term in ("Settings → Admin → Connections", "Chat Completions", "Responses", "gpt-5.4", "Docker"):
            self.assertIn(term, text)
        self.assertIn("docs.openwebui.com/getting-started/quick-start/connect-a-provider/starting-with-openai-compatible", text)
        self.assertNotIn("/v1/" + "tasks", text)

    def test_compose_requires_reviewed_image_and_secret(self):
        compose = (ROOT / "configs/docker-compose.yml").read_text(encoding="utf-8")
        self.assertIn("OPEN_WEBUI_IMAGE:?", compose)
        self.assertIn("OPENAI_API_KEY:?", compose)
        self.assertNotIn("sk-", compose)


if __name__ == "__main__":
    unittest.main()
