import sys
import unittest
from unittest.mock import patch

import run_ui


class RunUiTests(unittest.TestCase):
    def test_runs_uvicorn_with_reload_by_default(self):
        with patch.object(sys, "argv", ["run_ui.py", "--no-browser"]):
            with patch("run_ui.uvicorn.run") as run:
                run_ui.main()

        run.assert_called_once_with(
            "web_app:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            reload_includes=["*.py", "*.html", "*.css"],
        )

    def test_allows_disabling_reload(self):
        with patch.object(sys, "argv", ["run_ui.py", "--no-browser", "--no-reload"]):
            with patch("run_ui.uvicorn.run") as run:
                run_ui.main()

        run.assert_called_once_with(
            "web_app:app",
            host="127.0.0.1",
            port=8000,
            reload=False,
            reload_includes=["*.py", "*.html", "*.css"],
        )


if __name__ == "__main__":
    unittest.main()
