import os

from ..core.config import get_settings


class InterviewFilesRepository:
    """
    Repository for storing and retrieving interview text as .txt files
    under the OneDrive base path. File naming convention: {patient_id}.txt
    stored within the "Interview" folder.

    Notes:
    - The base path is configurable via ONEDRIVE_BASE_PATH.
    - This repo intentionally does not maintain any in-memory records.
    """

    def __init__(self) -> None:
        self.settings = get_settings()
        # Folder name as per requirement
        self.sub_folder_name = "Interview"

    def _folder_path(self) -> str:
        base = self.settings.ONEDRIVE_BASE_PATH
        # Ensure subdirectory exists
        path = os.path.join(base, self.sub_folder_name)
        os.makedirs(path, exist_ok=True)
        return path

    def _file_path(self, patient_id: str) -> str:
        safe_name = f"{patient_id}.txt"
        return os.path.join(self._folder_path(), safe_name)

    # PUBLIC_INTERFACE
    def write_text(self, patient_id: str, content: str) -> str:
        """Write interview text to OneDrive Interview folder using patient_id as filename."""
        full = self._file_path(patient_id)
        with open(full, "w", encoding="utf-8") as f:
            f.write(content or "")
        # Return relative path under OneDrive base for reference
        rel = os.path.relpath(full, self.settings.ONEDRIVE_BASE_PATH)
        return rel

    # PUBLIC_INTERFACE
    def read_text(self, patient_id: str) -> str:
        """Read interview text from OneDrive Interview folder."""
        full = self._file_path(patient_id)
        with open(full, "r", encoding="utf-8") as f:
            return f.read()

    # PUBLIC_INTERFACE
    def exists(self, patient_id: str) -> bool:
        """Check if an interview text file exists for a patient."""
        return os.path.exists(self._file_path(patient_id))

    # PUBLIC_INTERFACE
    def delete(self, patient_id: str) -> bool:
        """Delete the interview file for a patient if present."""
        full = self._file_path(patient_id)
        if os.path.exists(full):
            os.remove(full)
            return True
        return False


interview_files_repo = InterviewFilesRepository()
