import io
import unittest
from contextlib import redirect_stdout

from hmgr.ui.context import print_model_context


class ModelContextTests(unittest.TestCase):
    def test_displayed_model_context_is_exact_prompt(self):
        prompt = "## Task\n\nUse the supplied evidence."
        output = io.StringIO()
        with redirect_stdout(output):
            print_model_context(prompt, purpose="test")
        self.assertIn(prompt, output.getvalue())


if __name__ == "__main__":
    unittest.main()
