import unittest

from hmgr.context.models import RenderSection
from hmgr.context.rendering import render_sections


class ContextRenderingTests(unittest.TestCase):
    def test_render_sections_respects_character_budget(self):
        result = render_sections(
            [
                RenderSection("high", "12345", priority=10, truncatable=True),
                RenderSection("low", "67890", priority=1),
            ],
            max_chars=20,
        )
        self.assertLessEqual(len(result), 20)
        self.assertIn("<high>", result)
        self.assertNotIn("<low>", result)


if __name__ == "__main__":
    unittest.main()
