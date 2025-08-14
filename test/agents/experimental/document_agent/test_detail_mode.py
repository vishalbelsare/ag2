# seo_workflow.py
"""
Minimal FunctionTarget test wiring for a two-agent group chat.
"""

import os
from typing import Any, Optional

from dotenv import load_dotenv

from autogen import LLMConfig, ConversableAgent
from autogen.agentchat import initiate_group_chat
from autogen.agentchat.group import ContextVariables, AgentTarget, FunctionTarget, ReplyResult
from autogen.agentchat.group.patterns import DefaultPattern
from autogen.agents.experimental.document_agent import DocAgent
from autogen.agents.experimental.document_agent import InMemoryQueryEngine

load_dotenv()


def main(session_id: Optional[str] = None) -> dict:
    # LLM config
    cfg = LLMConfig(api_type="openai", model="gpt-4o", api_key=os.environ["OPENAI_API_KEY"])

    # Shared context
    ctx = ContextVariables(data={"variable": "value1"})

    inmemory_qe = InMemoryQueryEngine(llm_config=cfg)
    doc_agent = DocAgent(
        name="doc_agent",
        llm_config=cfg,
        query_engine=inmemory_qe
    )

    review_agent = ConversableAgent(
        name="review_agent",
        llm_config=cfg,
        system_message="Review the answers and provide a summary of the key findings.",
    )

    user_agent = ConversableAgent(
        name="user",
        human_input_mode="ALWAYS",
    )

    # Conversation pattern
    pattern = DefaultPattern(
        initial_agent=doc_agent,
        agents=[doc_agent, review_agent],
        user_agent=user_agent,
        context_variables=ctx,
        group_manager_args={"llm_config": cfg},
    )

    # Register after-work handoff
    doc_agent.handoffs.set_after_work(AgentTarget(review_agent))

    # Run
    initiate_group_chat(
        pattern=pattern,
        messages="""
        Ingest this document: https://ontheline.trincoll.edu/images/bookdown/sample-local-pdf.pdf

        And answer the following queries:
        1. How long is the document?
        2. Are the pages long or short, and what does it depend on?
        3. What language is the document mostly written in?
        """,
        max_rounds=60,
    )

    return {"session_id": session_id}


if __name__ == "__main__":
    main()
