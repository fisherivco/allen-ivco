"""Tests for env_loader — auto-loading from ~/.config/env/*.env."""
import os
import tempfile
from pathlib import Path
from unittest.mock import patch
from ivco_calc.env_loader import _parse_env_file, load_env, ensure_var


def test_parse_env_file_basic():
    """Parse simple KEY=value lines."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("FOO=bar\nBAZ=qux\n")
        f.flush()
        result = _parse_env_file(Path(f.name))
    assert result == {"FOO": "bar", "BAZ": "qux"}
    os.unlink(f.name)


def test_parse_env_file_with_comments_and_blanks():
    """Skip comments and blank lines."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("# comment\n\nKEY=value\n# another\n")
        f.flush()
        result = _parse_env_file(Path(f.name))
    assert result == {"KEY": "value"}
    os.unlink(f.name)


def test_parse_env_file_with_export_prefix():
    """Handle export prefix."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("export MY_VAR=hello\n")
        f.flush()
        result = _parse_env_file(Path(f.name))
    assert result == {"MY_VAR": "hello"}
    os.unlink(f.name)


def test_parse_env_file_with_quotes():
    """Strip surrounding quotes."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write('SINGLE=\'quoted\'\nDOUBLE="quoted"\n')
        f.flush()
        result = _parse_env_file(Path(f.name))
    assert result == {"SINGLE": "quoted", "DOUBLE": "quoted"}
    os.unlink(f.name)


def test_parse_env_file_nonexistent():
    """Return empty dict for missing files."""
    result = _parse_env_file(Path("/nonexistent/file.env"))
    assert result == {}


def test_load_env_does_not_overwrite_existing():
    """Existing env vars take precedence over .env files."""
    import ivco_calc.env_loader as mod
    old_loaded = mod._loaded
    mod._loaded = False

    os.environ["TEST_EXISTING_VAR"] = "original"
    with tempfile.TemporaryDirectory() as tmpdir:
        env_file = Path(tmpdir) / "test.env"
        env_file.write_text("TEST_EXISTING_VAR=overwritten\n")
        with patch.object(mod, "ENV_DIR", Path(tmpdir)):
            load_env(force=True)
    assert os.environ["TEST_EXISTING_VAR"] == "original"
    del os.environ["TEST_EXISTING_VAR"]
    mod._loaded = old_loaded


def test_ensure_var_raises_on_missing():
    """ensure_var raises ValueError with helpful message."""
    import ivco_calc.env_loader as mod
    old_loaded = mod._loaded
    mod._loaded = False

    os.environ.pop("NONEXISTENT_VAR_XYZ", None)
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(mod, "ENV_DIR", Path(tmpdir)):
            try:
                ensure_var("NONEXISTENT_VAR_XYZ")
                assert False, "Should have raised ValueError"
            except ValueError as e:
                assert "NONEXISTENT_VAR_XYZ" in str(e)
    mod._loaded = old_loaded
