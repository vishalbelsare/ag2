# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0

from copy import deepcopy
from typing import Any, Optional

from pydantic import BaseModel, Field

from .... import Agent, ConversableAgent, UpdateSystemMessage
from ....doc_utils import export_module
from ....oai.client import OpenAIWrapper

__all__ = ["EvaluationAgent"]


@export_module("autogen.agents.contrib")
class EvaluationAgent(ConversableAgent):
    """Utilises multiple agents, evaluating their performance then selecting and returning the best one."""

    # Internal process:
    # 1. Synthesize the task from the input
    # 2. Each agent gives their response
    # 3. Evaluator evaluates and selects the response
    # 4. Return the selected response

    DEFAULT_EVALUATOR_MESSAGE = (
        "You are responsible for evaluating and selecting the best response from a set of agents. "
        "Each agent, identified by a name, will be given a chance to respond. "
        "Evaluation Criteria:\n[evaluation_guidance]\n"
        "[agent_outputs]"
    )

    DEFAULT_EVALUATON_GUIDANCE = (
        "1. Carefully review each approach and result\n"
        "2. Evaluate each solution based on criteria appropriate to the task\n"
        "3. Select the absolute best response\n"
        "4. You must select a response as the best response"
    )

    def __init__(
        self,
        *,
        llm_config: dict[str, Any],
        agents: list[ConversableAgent],
        evaluation_guidance: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the EvaluationAgent.

        Args:
            llm_config (dict[str, Any]): LLM Configuration for the internal synthesizer and evaluator agents.
            agents (list[ConversableAgent]): List of agents that will provide their responses for evaluation.
            evaluation_guidance (str): Guidance on how to evaluate the agents, used by the internal evaluator agent.
            **kwargs (Any): Additional keyword arguments to pass to the base class.
        """

        assert len(agents) > 1, "EvaluationAgent requires at least two agents for evaluation."
        assert llm_config, "EvaluationAgent requires llm_config for the internal synthesizer and evaluator agents."

        # Initialise the base class, ignoring llm_config as we'll put that on internal agents
        super().__init__(**kwargs)

        # Store your custom parameters
        self._evaluation_agents = agents
        self._evaluation_llm_config = llm_config
        self._evaluation_guidance = evaluation_guidance if evaluation_guidance else self.DEFAULT_EVALUATON_GUIDANCE

        # Create agents
        self.create_evaluator()

        # Register our reply function for evaluation with the agent
        # This will be the agent's only reply function
        self.register_reply(
            trigger=[Agent, None], reply_func=self.generate_evaluate_reply, remove_other_reply_funcs=True
        )

    def generate_evaluator_system_message(self, agent: ConversableAgent, messages: list[dict[str, Any]]) -> str:
        """Generate the system message for the internal evaluator agent."""
        system_message = EvaluationAgent.DEFAULT_EVALUATOR_MESSAGE.replace(
            "[evaluation_guidance]", self._evaluation_guidance
        )

        # Compile the responses to the answers here.

        return system_message

    # Structured Output for the evaluator agent
    class NominatedResponse(BaseModel):
        agent_name: str = Field(description="Name of agent that provided the response.")
        response: str = Field(description="Exact, word-for-word, response selected.")
        reason: str = Field(description="Brief reason why it was the best response.")

    def create_evaluator(self) -> None:
        """Create the internal evaluator agent."""

        # Add the response_format to the agent
        evaluator_llm_config = deepcopy(self._evaluation_llm_config)
        evaluator_llm_config["response_format"] = EvaluationAgent.NominatedResponse

        self._evaluator_agent = ConversableAgent(
            name="evaluationagent_evaluator",
            llm_config=evaluator_llm_config,
            update_agent_state_before_reply=[UpdateSystemMessage(self.generate_evaluator_system_message)],
        )

    # Inner evaluation process
    def generate_evaluate_reply(
        self,
        agent: ConversableAgent,
        messages: Optional[list[dict[str, Any]]] = None,
        sender: Optional[Agent] = None,
        config: Optional[OpenAIWrapper] = None,
    ) -> tuple[bool, dict[str, Any]]:
        # Final reply, with the date/time as the message
        return True, {"content": "Tick, tock, the current date/time is."}
