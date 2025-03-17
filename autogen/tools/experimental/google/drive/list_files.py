# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0

# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0


from typing import Annotated, Any, Optional

from .....doc_utils import export_module
from .... import Depends, Tool
from ....dependency_injection import on
from ..authentication import build_service_from_db, build_service_from_json

__all__ = [
    "ListGoogleDriveFilesTool",
]


def _list_files(service: Any, page_size: int) -> Any:
    # Call the Drive v3 API
    results = service.files().list(pageSize=page_size, fields="nextPageToken, files(id, name)").execute()
    return results.get("files", [])


@export_module("autogen.tools.experimental")
class ListGoogleDriveFilesTool(Tool):
    """ListGoogleDriveFilesTool is a tool that uses the Google Drive API to list files in a user's Google Drive."""

    def __init__(
        self,
        client_secret_file: str,
        scopes: list[str],
        user_id: Optional[int] = None,
        db_engine_url: str = "sqlite:///database.db",
        users_token_file: str = "token.json",
    ):
        def list_google_drive_files(
            client_secret_file: Annotated[str, Depends(on(client_secret_file))],
            scopes: Annotated[list[str], Depends(on(scopes))],
            user_id: Annotated[Optional[int], Depends(on(user_id))],
            db_engine_url: Annotated[str, Depends(on(db_engine_url))],
            users_token_file: Annotated[str, Depends(on(users_token_file))],
            page_size: Annotated[int, "The number of files to list per page."] = 10,
        ) -> Any:
            if user_id is None:
                service = build_service_from_json(
                    client_secret_file=client_secret_file,
                    scopes=scopes,
                    service_name="drive",
                    users_token_file=users_token_file,
                )
            else:
                service = build_service_from_db(
                    client_secret_file=client_secret_file,
                    scopes=scopes,
                    user_id=user_id,
                    service_name="drive",
                    db_engine_url=db_engine_url,
                )

            return _list_files(service=service, page_size=page_size)

        super().__init__(
            name="list_google_drive_files",
            description="List files in a user's Google Drive.",
            func_or_tool=list_google_drive_files,
        )
