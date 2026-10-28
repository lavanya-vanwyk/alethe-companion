from unittest.mock import MagicMock, mock_open, patch

from src.domain.entities import CodeChangeDelta
from src.infrastructure.git_tracker import ASTGitTracker

# Mocked output of `git diff --cached -U0`
MOCK_DIFF_STDOUT = """diff --git a/dummy_service.py b/dummy_service.py
--- a/dummy_service.py
+++ b/dummy_service.py
@@ -2,2 +2,2 @@
-    def authenticate(self, user):
+    def authenticate(self, user, token):
"""

# Mocked Python source code corresponding to the diff
MOCK_SOURCE_CODE = """class AuthService:
    def authenticate(self, user, token):
        return True
"""


@patch("src.infrastructure.git_tracker.subprocess.run")
def test_ast_tracker_get_changed_lines(mock_subprocess_run):
    """Verifies that git diffs are correctly parsed into file and line numbers."""
    mock_result = MagicMock()
    mock_result.stdout = MOCK_DIFF_STDOUT
    mock_subprocess_run.return_value = mock_result

    tracker = ASTGitTracker()
    changed_lines = tracker._get_changed_lines()

    assert "dummy_service.py" in changed_lines
    # The start line from @@ -2,2 +2,2 @@ is +2, so it should extract 2
    assert changed_lines["dummy_service.py"] == [2]


@patch("src.infrastructure.git_tracker.subprocess.run")
@patch("builtins.open", new_callable=mock_open, read_data=MOCK_SOURCE_CODE)
def test_ast_tracker_structural_summaries(mock_file, mock_subprocess_run):
    """Verifies that mock diffs generate accurate semantic change logs."""
    mock_result = MagicMock()
    mock_result.stdout = MOCK_DIFF_STDOUT
    mock_subprocess_run.return_value = mock_result

    tracker = ASTGitTracker()
    deltas = tracker.get_structural_diffs()

    assert len(deltas) == 1
    delta = deltas[0]

    # Validate the CodeChangeDelta domain entity properties
    assert isinstance(delta, CodeChangeDelta)
    assert delta.file_path == "dummy_service.py"
    assert delta.changed_lines == [2]

    # AST parser should detect the Function Definition
    assert "Function Definition: 'authenticate'" in delta.structural_summary
