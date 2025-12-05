from unittest.mock import patch, call
from pynotes.main import PyNotes

class TestMain:
    @patch("pynotes.main.platform")
    @patch("pynotes.main.subprocess")
    def test_linux_defaults(
        self,
        mock_subprocess,
        mock_platform,
        monkeypatch
        ):
        """
        Test that linux defaults are loaded correctly.
        Also tests that other defaults are set correctly.
        """

        mock_subprocess.run.return_value = 0
        mock_platform.system.return_value = "Linux"
        
        monkeypatch.delenv("EDITOR", raising=False)

        app = PyNotes(config_path="fake_config.ini")
        assert app.platform == "Linux"
        assert app.editor == "nano"
        assert app.note_directory == "~/notes"
        assert app.default_extension == ".md"
        assert not app.use_git
        assert not app.auto_push

    
    def test_windows_defaults(self, monkeypatch):
        """
        Test that windows defaults are loaded correctly
        """

        monkeypatch.delenv("EDITOR", raising=False)

        with patch("platform.system", return_value="Windows"):
            app = PyNotes(config_path="fake_config.ini")

            assert app.platform == "Windows"
            assert app.editor == "notepad.exe"

    @patch("pynotes.main.subprocess")
    @patch("pynotes.main.datetime")
    def test_git_sync(self, mock_datetime, mock_subprocess, tmp_path):
        now = "2025-01-01 10:30:00"
        today = "2025-01-01"
        mock_datetime.datetime.now().strftime.return_value = now
        mock_datetime.datetime.today().strftime.return_value = today
        mock_subprocess.run.return_value = 0

        test_note_path = tmp_path / "notes"

        test_ini_path = tmp_path / "test.ini"
        test_ini_path.write_text(f"""
            [CORE]
            default_editor = nano
            note_directory = {str(test_note_path)}
            default_extension = .md
            [GIT]
            use_git = True
            auto_push = True
            """
            )

        app = PyNotes(config_path=str(test_ini_path))
        app.daily_note(args=None)
        
        expected_calls = [
            call(
                ["nano", f"{str(test_note_path)}/{today}.md"],
                check=True
                ),
            call(
                ["git", "add", "."],
                check=True, 
                cwd=str(test_note_path)
            ),
            call(
                ["git", "commit", "-m", f"PyNote Update: {now}"],
                check=True, 
                cwd=str(test_note_path),
                capture_output=True,
                text=True
            ),
            call(
                ["git", "push", "-u", "origin"],
                check=True, 
                cwd=str(test_note_path),
                capture_output=True,
                text=True
            ),
        ]

        mock_subprocess.run.assert_has_calls(expected_calls)
