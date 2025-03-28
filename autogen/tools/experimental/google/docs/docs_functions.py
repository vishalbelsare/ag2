# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0

import tempfile
from typing import Any, Optional

from markdown import markdown

from .....import_utils import optional_import_block, require_optional_import
from ..model import GoogleFileInfo
from .model import CreateDocsFile

with optional_import_block():
    from googleapiclient.http import MediaFileUpload


__all__ = [
    "list_folders_and_docs_files_f",
    "get_document_content_f",
    "create_empty_document_f",
    "create_document_with_content_f",
]


@require_optional_import(
    [
        "googleapiclient",
    ],
    "google-api",
)
def list_folders_and_docs_files_f(
    service: Any,
    page_size: int,
    folder_id: Optional[str],
) -> list[GoogleFileInfo]:
    doc_mime_types = [
        "application/vnd.google-apps.document",  # Google Docs
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # DOCX
        # Also allow folders to be listed
        "application/vnd.google-apps.folder",
    ]

    mime_type_filter = " or ".join(f"mimeType='{mime}'" for mime in doc_mime_types)
    query = f"({mime_type_filter}) and trashed=false"

    if folder_id:
        query = f"'{folder_id}' in parents and {query}"

    kwargs = {
        "pageSize": page_size,
        "fields": "nextPageToken, files(id, name, mimeType)",
        "q": query,  # Apply filtering in the query itself
    }

    response = service.files().list(**kwargs).execute()
    result = response.get("files", [])

    if not isinstance(result, list):
        raise ValueError(f"Expected a list of files, but got {result}")

    return [GoogleFileInfo(**file_info) for file_info in result]

@require_optional_import(
    [
        "googleapiclient",
    ],
    "google-api",
)
def get_document_content_f(service: Any, document_id: str) -> Any:
    document = service.documents().get(documentId=document_id).execute()
    return document


@require_optional_import(
    [
        "googleapiclient",
    ],
    "google-api",
)
def create_empty_document_f(service: Any, title: str) -> str:
    doc = service.documents().create(body={"title": title}).execute()
    return f"Document with ID {doc['documentId']} created."


@require_optional_import(
    [
        "googleapiclient",
    ],
    "google-api",
)
def create_document_with_content_f(service: Any, docs_file: CreateDocsFile) -> str:
    # Set metadata for the file
    file_metadata = {
        'name': docs_file.name,
        'mimeType': 'application/vnd.google-apps.document'  # Convert it to Google Docs
    }

    if docs_file.content_type == "markdown":
        # Convert the markdown content to HTML
        docs_file.content = markdown(docs_file.content)
        docs_file.content_type = "html"

    # Create a temporary file and write the HTML content to it
    with tempfile.NamedTemporaryFile(suffix=".html") as temp_html_file:
        temp_html_file.write(docs_file.content.encode("utf-8"))
        temp_html_file.flush()  # Ensure content is written before accessing the file
        temp_html_file.seek(0)  # Move the file pointer to the beginning of the file
        temp_html_file_path = temp_html_file.name

        # Upload the file to Google Drive with MIME type as 'text/html'
        media = MediaFileUpload(temp_html_file_path, mimetype='text/html')

        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

    return f'File uploaded successfully. Google Docs ID: {file["id"]}'
