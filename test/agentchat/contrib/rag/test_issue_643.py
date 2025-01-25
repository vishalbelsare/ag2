# Copyright (c) 2023 - 2025, Owners of https://github.com/ag2ai
#
# SPDX-License-Identifier: Apache-2.0


from autogen import ConversableAgent, UserProxyAgent
from autogen.agentchat.contrib.rag.parser_utils import docling_parse_docs
from autogen.import_utils import optional_import_block, skip_on_missing_imports
from autogen.tools.tool import Tool

from ....conftest import Credentials

with optional_import_block():
    import selenium  # noqa: F401
    import webdriver_manager  # noqa: F401


@skip_on_missing_imports(["selenium", "webdriver_manager"], "rag")
class TestIssue643:
    def test_issue_643(self, credentials_gpt_4o_mini: Credentials) -> None:
        llm_config = credentials_gpt_4o_mini.llm_config

        parser_tool = Tool(
            name="docling_parse_docs",
            description="Use this tool to parse and understand text.",
            func_or_tool=docling_parse_docs,
        )

        DEFALT_DOCLING_PARSER_PROMPT = """
        You are an expert in parsing and understanding text. You can use this tool to parse various documents and extract information from them.
        """

        class ParserAgent(ConversableAgent):
            def __init__(self):
                super().__init__(
                    name="DoclingParserAgent",
                    system_message=DEFALT_DOCLING_PARSER_PROMPT,
                    human_input_mode="TERMINATE",
                    llm_config=llm_config,
                )

                parser_tool.register_for_llm(self)

        user_agent = UserProxyAgent(
            name="UserAgent",
            human_input_mode="NEVER",
        )

        parser_tool.register_for_execution(user_agent)

        parser_agent = ParserAgent()

        user_agent.initiate_chat(
            parser_agent,
            message="could you parse /workspaces/ag2/test/agentchat/contrib/graph_rag/Toast_financial_report.pdf and output to /workspaces/ag2/output_dir_path?",
            max_turns=5,
        )
