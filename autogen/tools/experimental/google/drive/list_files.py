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
from ..service import build_service

with optional_import_block():
    from google.oauth2.credentials import Credentials

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
        "google_auth_oauthlib",
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

        def list_google_drive_files(
            page_size: Annotated[int, "The number of files to list per page."] = 10,
        ) -> Any:
            service = build_service(
                credentials=self.credentials,
                service_name="drive",
                version=self.api_version,
            )

            return _list_files(service=service, page_size=page_size)

        super().__init__(
            name="list_google_drive_files",
            description="List files in a user's Google Drive.",
            func_or_tool=list_google_drive_files,
        )
