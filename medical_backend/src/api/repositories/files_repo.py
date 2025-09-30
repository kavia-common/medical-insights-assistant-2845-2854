import os
from typing import Tuple

from ..core.config import get_settings


def _safe_join(base: str, relative_path: str) -> str:
    """
    Safely join a base path and a relative path, preventing path traversal.
    """
    target = os.path.normpath(os.path.join(base, relative_path))
    if not target.startswith(os.path.abspath(base)):
        raise ValueError("Invalid path; attempted path traversal detected.")
    return target


class FilesRepository:
    """
    Repository to read/write from OneDrive-synced and local storage paths.
    """

    def __init__(self) -> None:
        self.settings = get_settings()

    # PUBLIC_INTERFACE
    def read(self, relative_path: str, use_onedrive: bool = True) -> Tuple[str, str]:
        """Read text content from a file under the chosen base directory."""
        base = self.settings.ONEDRIVE_BASE_PATH if use_onedrive else self.settings.STORAGE_BASE_PATH
        full = _safe_join(base, relative_path)
        with open(full, "r", encoding="utf-8") as f:
            content = f.read()
        return relative_path, content

    # PUBLIC_INTERFACE
    def write(self, relative_path: str, content: str, use_onedrive: bool = True) -> str:
        """Write text content to a file under the chosen base directory."""
        base = self.settings.ONEDRIVE_BASE_PATH if use_onedrive else self.settings.STORAGE_BASE_PATH
        full = _safe_join(base, relative_path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)
        return relative_path


files_repo = FilesRepository()
