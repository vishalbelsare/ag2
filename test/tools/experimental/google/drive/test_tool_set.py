# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0


import unittest
from unittest.mock import MagicMock

from autogen import AssistantAgent, UserProxyAgent
from autogen.import_utils import optional_import_block, run_for_optional_imports, skip_on_missing_imports
from autogen.tools import ToolSet

with optional_import_block():
    from autogen.tools.experimental.google.authentication.credentials_local_provider import (
        GoogleCredentialsLocalProvider,
    )
    from autogen.tools.experimental.google.drive import GoogleDriveToolSet


from .....conftest import Credentials


@skip_on_missing_imports(
    [
        "googleapiclient",
        "google_auth_httplib2",
        "google_auth_oauthlib",
    ],
    "google-api",
)
class TestGoogleDriveToolSet:
    def test_init(self) -> None:
        with unittest.mock.patch(
            "autogen.tools.experimental.google.drive.tool_set.build",
            return_value=MagicMock(),
        ) as mock_build:
            tool_set = GoogleDriveToolSet(
                credentials=MagicMock(),
                download_folder="download_folder",
            )

            mock_build.assert_called_once()
            assert isinstance(tool_set, ToolSet)

            assert len(tool_set.tools) == 2

    @run_for_optional_imports("openai", "openai")
    def test_end2end(self, credentials_gpt_4o_mini: Credentials) -> None:
        user_proxy = UserProxyAgent(name="user_proxy", human_input_mode="NEVER")
        assistant = AssistantAgent(name="assistant", llm_config=credentials_gpt_4o_mini.llm_config)

        client_secret_file = "client_secret_ag2.json"
        scopes = [
            "https://www.googleapis.com/auth/drive.metadata.readonly",
            "https://www.googleapis.com/auth/drive.readonly",
            "https://www.googleapis.com/auth/drive.file",
        ]
        provider = GoogleCredentialsLocalProvider(
            client_secret_file=client_secret_file,
            scopes=scopes,
            users_token_file="token.json",
        )
        tool_set = GoogleDriveToolSet(
            credentials=provider.get_credentials(),
            download_folder="download_folder",
        )
        tool_set.register_for_execution(user_proxy)
        tool_set.register_for_llm(assistant)

        user_proxy.initiate_chat(
            recipient=assistant,
            # message="Get last 3 files from Google Drive",
            # message="Download second file from Google Drive",
            message="Download latest 5 files from Google Drive",
            max_turns=5,
        )
