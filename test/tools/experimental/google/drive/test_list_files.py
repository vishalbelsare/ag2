# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0


from autogen.tools.experimental.google import ListGoogleDriveFilesTool


class TestListGoogleDriveFilesTool:
    def test_init(self) -> None:
        google_drive_tool = ListGoogleDriveFilesTool(
            client_secret_file="secret.json",
            scopes=["https://www.googleapis.com/auth/drive.metadata.readonly"],
            user_id=1,
        )

        assert google_drive_tool.name == "list_google_drive_files"
        assert google_drive_tool.description == "List files in a user's Google Drive."

    def test_end2end(self, tmp_db_engine_url: str) -> None:
        client_secret_file = "client_secret_ag2.json"
        google_drive_tool = ListGoogleDriveFilesTool(
            client_secret_file=client_secret_file,
            scopes=["https://www.googleapis.com/auth/drive.metadata.readonly"],
            user_id=1,
            db_engine_url=tmp_db_engine_url,
        )

        result = google_drive_tool.func(10)
        print(f"List of files: {result}")
