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

    def __init__(self, tools: dict[str, Tool]) -> None:
        """Create a new ToolMap object.

        Args:
            tools (dict[str, Tool]): A dictionary of tools to include in the set.
        """
        self.tools = tools

    def register_for_llm(self, agent: "ConversableAgent") -> None:
        """Register the tools in the set with an LLM agent.

        Args:
            agent (ConversableAgent): The LLM agent to register the tools with.
        """
        for tool in self.tools.values():
            tool.register_for_llm(agent)

    def register_for_execution(self, agent: "ConversableAgent") -> None:
        """Register the tools in the set with an agent for

        Args:
            agent (ConversableAgent): The agent to register the tools with.
        """
        for tool in self.tools.values():
            tool.register_for_execution(agent)
