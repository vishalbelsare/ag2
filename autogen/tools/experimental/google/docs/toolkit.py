# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path
from typing import Annotated, Any, Literal, Optional, Union

from .....doc_utils import export_module
from .....import_utils import optional_import_block
from .... import Tool, Toolkit, tool
from ..model import GoogleFileInfo
from .model import CreateDocsFile
from ..toolkit_protocol import GoogleToolkitProtocol
from .docs_functions import list_folders_and_docs_files_f, get_document_content_f, create_empty_document_f, create_document_with_content_f

with optional_import_block():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

__all__ = [
    "GoogleDocsToolkit",
]


@export_module("autogen.tools.experimental.google.drive")
class GoogleDocsToolkit(Toolkit, GoogleToolkitProtocol):
    """A toolkit for Google Docs."""

    def __init__(  # type: ignore[no-any-unimported]
        self,
        *,
        credentials: "Credentials",
        download_folder: Union[Path, str],
        exclude: Optional[list[Literal["list_folders_and_docs_files", "get_document_content", "create_empty_document", "create_document_with_content"]]] = None,
        docs_api_version: str = "v1",
        drive_api_version: str = "v3",
    ) -> None:
        """Initialize the Google Docs toolkit.

        Args:
            credentials: The Google OAuth2 credentials.
            download_folder: The folder to download files to.
            exclude: The tool names to exclude.
            docs_api_version: The Google Docs API version to use."
            drive_api_version: The Google Drive API version to
        """
        self.docs_service = build(serviceName="docs", version=docs_api_version, credentials=credentials)
        self.drive_service = build(serviceName="drive", version=drive_api_version, credentials=credentials)

        if isinstance(download_folder, str):
            download_folder = Path(download_folder)
        download_folder.mkdir(parents=True, exist_ok=True)

        @tool(description="List folders and docs files in a Google Drive")
        def list_folders_and_docs_files(
            page_size: Annotated[int, "The number of files to list per page."] = 10,
            folder_id: Annotated[
                Optional[str],
                "The ID of the folder to list files from. If not provided, lists all files in the root folder.",
            ] = None,
        ) -> list[GoogleFileInfo]:
            return list_folders_and_docs_files_f(service=self.drive_service, page_size=page_size, folder_id=folder_id)

        @tool(description="Get the content of a Google Docs document")
        def get_document_content(
            document_id: Annotated[str, "The ID of the document to get the content from."]
        ) -> Any:
            # TODO: Add a return type hint
            return get_document_content_f(service=self.docs_service, document_id=document_id)

        @tool(description="Create an empty Google Docs document")
        def create_empty_document(
            title: Annotated[str, "The title of the document to create."]
        ) -> str:
            return create_empty_document_f(service=self.docs_service, title=title)

        @tool(description="Create a Google Docs document with content")
        def create_document_with_content(
            docs_file: Annotated[CreateDocsFile, "The file to create."]
        ) -> str:
            return create_document_with_content_f(service=self.drive_service, docs_file=docs_file)

        if exclude is None:
            exclude = []

        tools = [
            tool for tool in [list_folders_and_docs_files, get_document_content, create_empty_document, create_document_with_content] if tool.name not in exclude
        ]
        super().__init__(tools=tools)


    @classmethod
    def recommended_docs_scopes(cls) -> list[str]:
        """Return the recommended scopes manatory for using docs tools from this toolkit."""
        return [
            "https://www.googleapis.com/auth/documents.readonly",
        ]

    @classmethod
    def recommended_drive_scopes(cls) -> list[str]:
        """Return the recommended scopes manatory for using drive tools from this toolkit."""
        return [
            "https://www.googleapis.com/auth/drive",
        ]


    @classmethod
    def recommended_scopes(cls) -> list[str]:
        """Return the recommended scopes manatory for using all the tools from this toolkit."""
        return cls.recommended_docs_scopes() + cls.recommended_drive_scopes()
