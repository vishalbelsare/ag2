# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path
from typing import Annotated, Literal, Optional, Union

from .....import_utils import optional_import_block
from .....tools import ToolSet, tool
from ..model import GoogleFileInfo
from .drive_functions import download_file, list_files

with optional_import_block():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

__all__ = [
    "GoogleDriveToolSet",
]


class GoogleDriveToolSet(ToolSet):
    def __init__(
        self,
        *,
        credentials: "Credentials",
        download_folder: Union[Path, str],
        exclude: Optional[list[Literal["list_files_in_folder", "download_file", "upload_file"]]] = None,
        api_version: str = "v3",
    ) -> None:
        self.credentials = credentials
        self.api_version = api_version
        self.service = build(serviceName="drive", version=api_version, credentials=credentials)

        if isinstance(download_folder, str):
            download_folder = Path(download_folder)
        download_folder.parent.mkdir(parents=True, exist_ok=True)

        tools_list = []

        @tool(description="list all files in a Google Drive folder")
        def list_files_in_folder(
            page_size: Annotated[int, "The number of files to list per page."] = 10,
            folder_path: Annotated[
                Optional[str],
                "The path of the folder to list files in. If not provided, lists files in the root folder.",
            ] = None,
        ) -> list[GoogleFileInfo]:
            return list_files(service=self.service, page_size=page_size)

        @tool(description="download a file from Google Drive")
        def download_file_from_drive(
            file_id: Annotated[str, "The ID of the file to download."],
            mime_type: Annotated[
                Literal[
                    "application/pdf",
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    "text/plain",
                    "application/rtf",
                ],
                "The MIME type of the file to download.",
            ],
        ) -> str:
            return download_file(
                service=self.service, file_id=file_id, mime_type=mime_type, download_folder=download_folder
            )

        if exclude is None:
            exclude = []

        tools_list = [tool for tool in [list_files_in_folder, download_file_from_drive] if tool.name not in exclude]
        super().__init__(tools=tools_list)
