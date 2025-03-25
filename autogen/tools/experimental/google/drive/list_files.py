# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0

# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0


from typing import Annotated, Any

from .....doc_utils import export_module
from .....import_utils import optional_import_block, require_optional_import
from .... import Tool

with optional_import_block():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build


__all__ = [
    "ListGoogleDriveFilesTool",
]


@require_optional_import(
    [
        "googleapiclient",
    ],
    "google-api",
)
def _list_files(service: Any, page_size: int) -> Any:
    # Call the Drive v3 API
    results = service.files().list(pageSize=page_size, fields="nextPageToken, files(id, name)").execute()
    return results.get("files", [])


@require_optional_import(
    [
        "googleapiclient",
        "google_auth_httplib2",
    ],
    "google-api",
)
@export_module("autogen.tools.experimental")
class ListGoogleDriveFilesTool(Tool):
    """ListGoogleDriveFilesTool is a tool that uses the Google Drive API to list files in a user's Google Drive."""

    def __init__(
        self,
        credentials: "Credentials",
        api_version: str = "v3",
    ):
        self.credentials = credentials
        self.api_version = api_version
        self.service = build(serviceName="drive", version=api_version, credentials=credentials)

        def list_google_drive_files(
            page_size: Annotated[int, "The number of files to list per page."] = 10,
        ) -> Any:
            return _list_files(service=self.service, page_size=page_size)

        super().__init__(
            name="list_google_drive_files",
            description="List files in a user's Google Drive.",
            func_or_tool=list_google_drive_files,
        )
