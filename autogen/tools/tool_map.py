# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0

from typing import TYPE_CHECKING

from ..doc_utils import export_module
from .tool import Tool

if TYPE_CHECKING:
    from ..agentchat.conversable_agent import ConversableAgent

__all__ = ["ToolMap"]


@export_module("autogen.tools")
class ToolMap:
    """A class representing a set of tools that can be used by an agent for various tasks."""

    def __init__(self, tool_map: dict[str, Tool]) -> None:
        """Create a new ToolMap object.

        Args:
            tool_map (dict[str, Tool]): A dictionary of tools in the set.
        """
        self.tools_map = tool_map

    @property
    def tools(self) -> list[Tool]:
        """Get the list of tools in the set."""
        return list(self.tools_map.values())

    def register_for_llm(self, agent: "ConversableAgent") -> None:
        """Register the tools in the set with an LLM agent.

        Args:
            agent (ConversableAgent): The LLM agent to register the tools with.
        """
        for tool in self.tools_map.values():
            tool.register_for_llm(agent)

    def register_for_execution(self, agent: "ConversableAgent") -> None:
        """Register the tools in the set with an agent for

        Args:
            agent (ConversableAgent): The agent to register the tools with.
        """
        for tool in self.tools_map.values():
            tool.register_for_execution(agent)

    def get_tool(self, tool_name: str) -> Tool:
        """Get a tool from the set by name.

        Args:
            tool_name (str): The name of the tool to get.

        Returns:
            Tool: The tool with the given name.
        """
        if tool_name in self.tools_map:
            return self.tools_map[tool_name]

        raise ValueError(f"Tool '{tool_name}' not found in ToolMap.")

    def set_tool(self, tool: Tool) -> None:
        """Set a tool in the set.

        Args:
            tool (Tool): The tool to set.
        """
        self.tools_map[tool.name] = tool

    def remove_tool(self, tool_name: str) -> None:
        """Remove a tool from the set by name.

        Args:
            tool_name (str): The name of the tool to remove.
        """
        if tool_name in self.tools_map:
            del self.tools_map[tool_name]
        else:
            raise ValueError(f"Tool '{tool_name}' not found in ToolMap.")

    def __len__(self) -> int:
        """Get the number of tools in the map."""
        return len(self.tools_map)
