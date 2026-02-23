"""Auto-load environment variables from ~/.config/env/*.env files.

Follows Allen's credential storage convention: one .env file per service,
all in ~/.config/env/ with chmod 600.

Format: KEY=value (one per line, # comments allowed, blank lines skipped).
"""
import os
from pathlib import Path

_loaded = False

ENV_DIR = Path.home() / ".config" / "env"

# Map of env var names to the .env files that contain them
KNOWN_SOURCES = {
    "FMP_API_KEY": ["fmp.env", "global.env"],
    "DATABASE_URL": ["supabase.env"],
    "TAVILY_API_KEY": ["tavily.env"],
    "X_BEARER_TOKEN": ["global.env"],
}


def _parse_env_file(path: Path) -> dict[str, str]:
    """Parse a simple .env file into a dict."""
    result = {}
    if not path.exists():
        return result
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        # Strip optional quotes
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]
        # Handle export prefix
        if key.startswith("export "):
            key = key[7:].strip()
        result[key] = value
    return result


def load_env(force: bool = False) -> None:
    """Load all .env files from ~/.config/env/ into os.environ.

    Only sets variables that are not already set (environment takes precedence).
    Safe to call multiple times — skips if already loaded unless force=True.
    """
    global _loaded
    if _loaded and not force:
        return

    if not ENV_DIR.is_dir():
        _loaded = True
        return

    for env_file in sorted(ENV_DIR.glob("*.env")):
        try:
            pairs = _parse_env_file(env_file)
            for key, value in pairs.items():
                if key not in os.environ:
                    os.environ[key] = value
        except (PermissionError, OSError):
            continue

    _loaded = True


def ensure_var(name: str) -> str:
    """Load env files if needed, then return the value of a variable.

    Raises ValueError if the variable is not set after loading.
    """
    load_env()
    value = os.environ.get(name, "")
    if not value:
        sources = KNOWN_SOURCES.get(name, ["<unknown>.env"])
        raise ValueError(
            f"{name} not set. Expected in: {', '.join(sources)} "
            f"(under {ENV_DIR}/)"
        )
    return value
