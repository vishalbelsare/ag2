# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0


import tempfile
import unittest
from unittest.mock import MagicMock

import pytest

from autogen import AssistantAgent, UserProxyAgent
from autogen.import_utils import optional_import_block, run_for_optional_imports, skip_on_missing_imports
from autogen.tools import Toolkit

with optional_import_block():
    from autogen.tools.experimental.google.authentication.credentials_local_provider import (
        GoogleCredentialsLocalProvider,
    )
    from autogen.tools.experimental.google.docs import GoogleDocsToolkit


from .....conftest import Credentials


@skip_on_missing_imports(
    [
        "googleapiclient",
        "google_auth_httplib2",
        "google_auth_oauthlib",
    ],
    "google-api",
)
class TestGoogleDocsToolkit:
    def test_init(self) -> None:
        with unittest.mock.patch(
            "autogen.tools.experimental.google.docs.toolkit.build",
            return_value=MagicMock(),
        ) as mock_build:
            toolkit = GoogleDocsToolkit(
                credentials=MagicMock(),
                download_folder="download_folder",
            )

            assert mock_build.call_count == 2
            assert isinstance(toolkit, Toolkit)

            assert len(toolkit) == 4

    @pytest.mark.skip(reason="This test requires real google credentials and is not suitable for CI at the moment")
    @run_for_optional_imports("openai", "openai")
    def test_end2end(self, credentials_gpt_4o_mini: Credentials) -> None:
        user_proxy = UserProxyAgent(name="user_proxy", human_input_mode="NEVER")
        assistant = AssistantAgent(name="assistant", llm_config=credentials_gpt_4o_mini.llm_config)

        client_secret_file = "client_secret_ag2.json"
        provider = GoogleCredentialsLocalProvider(
            client_secret_file=client_secret_file,
            scopes=GoogleDocsToolkit.recommended_scopes(),
            token_file="token.json",
        )

        with tempfile.TemporaryDirectory() as tempdir:
            toolkit = GoogleDocsToolkit(
                credentials=provider.get_credentials(),
                download_folder=str(tempdir),
            )
            toolkit.register_for_execution(user_proxy)
            toolkit.register_for_llm(assistant)

            user_proxy.initiate_chat(
                recipient=assistant,
                # message="Get last 5 files from Google Drive and create a new document with title 'Last 5 files' and add the file names to the document",
                message="Write the summary of the last file into a new document. Name it 'Summary name_of_the_last_file'",
                max_turns=5,
            )
