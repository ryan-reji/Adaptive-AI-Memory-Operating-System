from pydantic import BaseModel, Field


class PermissionModeRequest(BaseModel):
    mode: str = Field(
        min_length=1,
        max_length=20,
    )


class FolderRequest(BaseModel):
    path: str = Field(
        min_length=1,
        max_length=4096,
    )


class ProjectFolderRequest(BaseModel):
    path: str = Field(
        min_length=1,
        max_length=4096,
    )
    project_name: str | None = Field(
        default=None,
        max_length=200,
    )


class PermissionModeResponse(BaseModel):
    mode: str


class FolderResponse(BaseModel):
    path: str


class ProjectFolderResponse(BaseModel):
    path: str
    project_name: str | None = None