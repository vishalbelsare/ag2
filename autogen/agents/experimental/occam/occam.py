# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0


import os
from typing import Optional, Union

from autogen.agentchat import Agent, ConversableAgent
from autogen.oai import OpenAIWrapper
from autogen.doc_utils import export_module
from autogen.io.base import IOStream
from autogen.messages.agent_messages import (
    TerminationAndHumanReplyMessage,
)

from occam_core.agents.model import AgentIOModel, OccamLLMMessage
from occamai.api_client import OccamClient
from occamai.api_client import AgentInstanceParamsModel, AgentRunDetail


__all__ = ["OccamAgent"]


@export_module("autogen.agents")
class OccamAgent(ConversableAgent):
    def _convert_ag_messages_to_agent_io_model(self, messages: list[dict]) -> AgentIOModel:
        return AgentIOModel(
            chat_messages=[
                OccamLLMMessage(
                    role=message["role"],
                    content=message["content"]
                )
                for message in messages
            ]
        )

    def occam_reply_func(
        self,
        messages: Optional[list[dict]] = None,
        sender: Optional[Agent] = None,
        config: Optional[OpenAIWrapper] = None,
    ) -> tuple[bool, Union[str, dict, None]]:
        """
        TODO:
        - Support path of resume, can do by ping before running the agent.
        - Some errors should be fashioned as communication, not raise errors, e.g. out of quota.
        Auto-resume considerations:
        * Auto-resume when topped up after an auto-pause, we don't have control over the workflow that the agent is running within.
        * Don't auto-resume and rely on user to always resume.
        """

        # TODO: Convert messages to AgentIOModel
        agent_io_model = self._convert_ag_messages_to_agent_io_model(messages)

        agent_run_detail: AgentRunDetail = self.occam_client.agents.run_agent(
            agent_instance_id=self.occam_agent_instance_id,
            sync=True,
            agent_input_model=agent_io_model,
        )
        print(f"Agent run status: {agent_run_detail.status}")
        print(f"Agent run result: {agent_run_detail.result}")

        agent_output = agent_run_detail.result

        # Send a message to the user to notify them it's waiting. Create a message as needed
        # iostream = IOStream.get_default()
        # iostream.send(
        #     TerminationAndHumanReplyMessage(no_human_input_msg="Dummy message", sender=sender, recipient=self)
        # )

        # True indicates final reply, string goes back into the chat's messages.
        return True, "".join([m.content for m in agent_output.chat_messages])

    def __init__(
        self,
        api_key: str,
        agent_params: Optional[AgentInstanceParamsModel] = AgentInstanceParamsModel(),
        base_url: str = "https://api.occam.ai",
        *args,
        **kwargs,
    ) -> None:
        """Initialize the Occam Agent.

        Args:
            llm_config (dict[str, Any]): The LLM configuration.
        """

        super().__init__(*args, **kwargs)
        self.occam_client = OccamClient(api_key=api_key, base_url=base_url)

        # Initialise agent.
        occam_agent_instance = self.occam_client.agents.instantiate_agent(
            agent_name="DeepSeek: R1 Distill Llama 70B",
            agent_params=agent_params
        )
        self.occam_agent_instance_id = occam_agent_instance.agent_instance_id
        print(f"Created Occam Agent instance: {self.occam_agent_instance_id}")

        # TODO: Remove below code, it's in the reply_func
        # agent_run_detail: AgentRunDetail = self.occam_client.agents.run_agent(
        #     agent_instance_id=self.occam_agent_instance_id,
        #     sync=True,
        #     agent_input_model=AgentIOModel(
        #         chat_messages=[
        #             OccamLLMMessage(
        #                 role="user",
        #                 content="Hello, tell me an interesting fact about the moon."
        #             )
        #         ]
        #     )
        # )
        # print(f"Agent run status: {agent_run_detail.status}")
        # print(f"Agent run result: {agent_run_detail.result}")

        self.register_reply(
            trigger=[Agent, None],
            reply_func=self.occam_reply_func,
            remove_other_reply_funcs=True,
        )


if __name__ == "__main__":
    api_key = os.getenv("OCCAM_API_KEY")
    base_url = os.getenv("OCCAM_BASE_URL")

    agent = OccamAgent(api_key=api_key, base_url=base_url, name="occam-agent")
    agent.initiate_chat(
        recipient=agent,
        message="Hello, tell me an interesting fact about the moon."
    )
