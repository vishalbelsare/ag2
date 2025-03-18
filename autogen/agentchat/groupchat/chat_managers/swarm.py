# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0
#
# Portions derived from  https://github.com/microsoft/autogen are under the MIT License.
# SPDX-License-Identifier: MIT
from typing import TYPE_CHECKING, Any, Callable, Optional, Union

from autogen.agentchat.contrib.swarm_agent import AfterWorkOption, a_initiate_swarm_chat, initiate_swarm_chat
from autogen.agentchat.conversable_agent import ConversableAgent
from autogen.agentchat.groupchat.groupchat import GroupChat

if TYPE_CHECKING:
    from ...agent import Agent, LLMMessageType
    from ...chat import ChatResult


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
