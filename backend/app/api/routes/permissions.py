from fastapi import APIRouter, HTTPException, Query

from backend.app.schemas.permissions import (
    FolderRequest,
    FolderResponse,
    PermissionModeRequest,
    PermissionModeResponse,
    ProjectFolderRequest,
    ProjectFolderResponse,
)
from backend.app.services.permissions_service import (
    add_file_allowed_folder,
    add_file_exclusion,
    add_file_project_folder,
    get_allowed_folders,
    get_exclusions,
    get_mode,
    get_project_folders,
    remove_file_allowed_folder,
    remove_file_exclusion,
    remove_file_project_folder,
    set_mode,
)


router = APIRouter(
    prefix="/permissions",
    tags=["Permissions"],
)


@router.get(
    "/mode",
    response_model=PermissionModeResponse,
)
def get_permission_mode_endpoint():
    return {
        "mode": get_mode(),
    }


@router.put(
    "/mode",
    response_model=PermissionModeResponse,
)
def set_permission_mode_endpoint(
    request: PermissionModeRequest,
):
    try:
        mode = set_mode(request.mode)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return {
        "mode": mode,
    }


@router.get(
    "/exclusions",
    response_model=list[FolderResponse],
)
def get_exclusions_endpoint():
    return get_exclusions()


@router.post(
    "/exclusions",
    response_model=FolderResponse,
)
def add_exclusion_endpoint(
    request: FolderRequest,
):
    return add_file_exclusion(request.path)


@router.delete(
    "/exclusions",
    status_code=204,
)
def remove_exclusion_endpoint(
    path: str = Query(
        min_length=1,
        max_length=4096,
    ),
):
    remove_file_exclusion(path)


@router.get(
    "/allowed-folders",
    response_model=list[FolderResponse],
)
def get_allowed_folders_endpoint():
    return get_allowed_folders()


@router.post(
    "/allowed-folders",
    response_model=FolderResponse,
)
def add_allowed_folder_endpoint(
    request: FolderRequest,
):
    return add_file_allowed_folder(request.path)


@router.delete(
    "/allowed-folders",
    status_code=204,
)
def remove_allowed_folder_endpoint(
    path: str = Query(
        min_length=1,
        max_length=4096,
    ),
):
    remove_file_allowed_folder(path)


@router.get(
    "/project-folders",
    response_model=list[ProjectFolderResponse],
)
def get_project_folders_endpoint():
    return get_project_folders()


@router.post(
    "/project-folders",
    response_model=ProjectFolderResponse,
)
def add_project_folder_endpoint(
    request: ProjectFolderRequest,
):
    return add_file_project_folder(
        request.path,
        project_name=request.project_name,
    )


@router.delete(
    "/project-folders",
    status_code=204,
)
def remove_project_folder_endpoint(
    path: str = Query(
        min_length=1,
        max_length=4096,
    ),
):
    remove_file_project_folder(path)