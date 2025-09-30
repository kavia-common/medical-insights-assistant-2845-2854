from fastapi import APIRouter, Query, HTTPException
from ..models.schemas import FileWriteRequest, FileReadResponse, OperationStatus
from ..repositories.files_repo import files_repo

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/write", response_model=OperationStatus, summary="Write file", description="Write a text file under OneDrive or local storage.")
# PUBLIC_INTERFACE
def write_file(payload: FileWriteRequest, use_onedrive: bool = Query(True, description="Write under OneDrive base path")) -> OperationStatus:
    """Write text content to a file."""
    try:
        rel = files_repo.write(payload.relative_path, payload.content, use_onedrive=use_onedrive)
        return OperationStatus(status="ok", detail=f"wrote:{rel}")
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@router.get("/read", response_model=FileReadResponse, summary="Read file", description="Read a text file under OneDrive or local storage.")
# PUBLIC_INTERFACE
def read_file(relative_path: str = Query(..., description="Relative path under base folder"),
              use_onedrive: bool = Query(True, description="Read from OneDrive base path")) -> FileReadResponse:
    """Read text content from a file."""
    try:
        rel, content = files_repo.read(relative_path, use_onedrive=use_onedrive)
        return FileReadResponse(relative_path=rel, content=content)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
