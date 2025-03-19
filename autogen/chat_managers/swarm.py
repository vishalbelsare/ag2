# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0

from typing import TYPE_CHECKING, Any, Callable, Optional, Union

from ..agentchat import ConversableAgent
from ..agentchat.contrib.swarm_agent import AfterWorkOption, a_initiate_swarm_chat, initiate_swarm_chat
from ..agentchat.groupchat import GroupChat
from ..doc_utils import export_module

if TYPE_CHECKING:
    from ..agentchat import Agent, ChatResult, LLMMessageType
    from .chat_manager import ChatManagerProtocol


@export_module("autogen.chat_managers")
class SwarmChatManager:
    def __init__(
        self,
        llm_config: dict[str, str],
        max_rounds: int = 20,
        context_variables: Optional[dict[str, Any]] = None,
        after_work: Optional[
            Union[
                AfterWorkOption,
                Callable[
                    [ConversableAgent, list[dict[str, Any]], GroupChat], Union[AfterWorkOption, ConversableAgent, str]
                ],
            ]
        ] = AfterWorkOption.TERMINATE,
        exclude_transit_message: bool = True,
    ):
        self.llm_config = llm_config
        self.after_work = after_work
        self.max_rounds = max_rounds
        self.context_variables = context_variables
        self.exclude_transit_message = exclude_transit_message

    def run(
        self,
        *agents: "Agent",
        message: str,
        messages: list["LLMMessageType"],
    ) -> "ChatResult":
        result, _, _ = initiate_swarm_chat(
            initial_agent=agents[0],
            agents=list(agents),
            messages=message if len(messages) == 0 else [*messages, {"role": "user", "content": message}],
            max_rounds=self.max_rounds,
            swarm_manager_args={"llm_config": self.llm_config},
            after_work=self.after_work,
            context_variables=self.context_variables,
            exclude_transit_message=self.exclude_transit_message,
        )

        return result

    async def a_run(
        self,
        *agents: "Agent",
        message: str,
        messages: list["LLMMessageType"],
    ) -> "ChatResult":
        result, _, _ = await a_initiate_swarm_chat(
            initial_agent=agents[0],
            agents=list(agents),
            messages=message if len(messages) == 0 else [*messages, message],
            max_rounds=self.max_rounds,
            swarm_manager_args={"llm_config": self.llm_config},
            after_work=self.after_work,
            context_variables=self.context_variables,
            exclude_transit_message=self.exclude_transit_message,
        )

        return result


if TYPE_CHECKING:

    def check_group_chat_manager_implements_chat_manager_protocol(x: SwarmChatManager) -> ChatManagerProtocol:
        return x
