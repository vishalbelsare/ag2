# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0

import pytest

from autogen.agentchat import ConversableAgent
from autogen.tools import ToolMap, tool

from ..conftest import Credentials


class TestToolMap:
    @pytest.fixture
    def tool_map(self) -> ToolMap:
        @tool(description="This is f1")
        def f1() -> None:
            pass

        @tool(description="This is f2")
        def f2() -> None:
            pass

        return ToolMap({"f1": f1, "f2": f2})

    def test_len(self, tool_map: ToolMap) -> None:
        assert len(tool_map) == 2

    def test_get_tool(self, tool_map: ToolMap) -> None:
        tool = tool_map.get_tool("f1")
        assert tool.description == "This is f1"

        with pytest.raises(ValueError, match="Tool 'f3' not found in ToolMap."):
            tool_map.get_tool("f3")

    def test_remove_tool(self, tool_map: ToolMap) -> None:
        tool_map.remove_tool("f1")
        with pytest.raises(ValueError, match="Tool 'f1' not found in ToolMap."):
            tool_map.get_tool("f1")

    def test_set_tool(self, tool_map: ToolMap) -> None:
        @tool(description="This is f3")
        def f3() -> None:
            pass

        tool_map.set_tool(f3)
        assert len(tool_map) == 3
        f3_tool = tool_map.get_tool("f3")
        assert f3_tool.description == "This is f3"

    def test_register_for_execution(self, tool_map: ToolMap) -> None:
        agent = ConversableAgent(
            name="test_agent",
        )
        tool_map.register_for_execution(agent)
        assert len(agent.function_map) == 2

    def test_register_for_llm(self, tool_map: ToolMap, mock_credentials: Credentials) -> None:
        agent = ConversableAgent(name="test_agent", llm_config=mock_credentials.llm_config)
        tool_map.register_for_llm(agent)
        expected_schema = [
            {
                "type": "function",
                "function": {
                    "description": "This is f1",
                    "name": "f1",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                },
            },
            {
                "type": "function",
                "function": {
                    "description": "This is f2",
                    "name": "f2",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                },
            },
        ]
        assert agent.llm_config["tools"] == expected_schema  # type: ignore[index]
