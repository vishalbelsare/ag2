# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path
from typing import Annotated, Literal, Optional, Union

from .....import_utils import optional_import_block
from .....tools import ToolMap, tool
from ..model import GoogleFileInfo
from .drive_functions import download_file, list_files_and_folders

with optional_import_block():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

__all__ = [
    "GoogleDriveToolMap",
]


class GoogleDriveToolMap(ToolMap):
    def __init__(
        self,
        *,
        credentials: "Credentials",
        download_folder: Union[Path, str],
        exclude: Optional[list[Literal["list_drive_files_and_folders", "download_file_from_drive"]]] = None,
        api_version: str = "v3",
    ) -> None:
        self.credentials = credentials
        self.api_version = api_version
        self.service = build(serviceName="drive", version=api_version, credentials=credentials)

        if isinstance(download_folder, str):
            download_folder = Path(download_folder)
        download_folder.mkdir(parents=True, exist_ok=True)

        @tool(description="List files and folders in a Google Drive")
        def list_drive_files_and_folders(
            page_size: Annotated[int, "The number of files to list per page."] = 10,
            folder_id: Annotated[
                Optional[str],
                "The ID of the folder to list files from. If not provided, lists all files in the root folder.",
            ] = None,
        ) -> list[GoogleFileInfo]:
            return list_files_and_folders(service=self.service, page_size=page_size, folder_id=folder_id)

        @tool(description="download a file from Google Drive")
        def download_file_from_drive(
            file_id: Annotated[str, "The ID of the file to download."],
            file_name: Annotated[str, "The name of the file to download. Folders are NOT supported."],
            mime_type: Annotated[
                str,
                "The MIME type of the file to download.",
            ],
        ) -> str:
            return download_file(
                service=self.service,
                file_id=file_id,
                file_name=file_name,
                mime_type=mime_type,
                download_folder=download_folder,
            )

        if exclude is None:
            exclude = []

        tools = {
            tool.name: tool
            for tool in [list_drive_files_and_folders, download_file_from_drive]
            if tool.name not in exclude
        }
        super().__init__(tools=tools)
