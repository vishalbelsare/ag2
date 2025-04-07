import os

from occam_core.agents.params import MultiAgentWorkspaceParamsModel, ChatMode
from occamai.api_client import OccamClient

from autogen.agentchat.conversable_agent import ConversableAgent
from autogen.agents.experimental.occam.occam import OccamAgent



if __name__ == "__main__":
    api_key = os.getenv("OCCAM_API_KEY")
    base_url = os.getenv("OCCAM_BASE_URL", "https://api.occam.ai")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    occam_client = OccamClient(api_key=api_key, base_url=base_url)
    agents_catalogue = occam_client.agents.get_agents_catalogue()
    print(f"Found {len(agents_catalogue)} agents in the catalogue.")

    agent_params = MultiAgentWorkspaceParamsModel(
        agents={
            "OpenAI: GPT-4": None,
            "mo": None,
        },
        max_chat_steps=30,
        agent_selection_rule=ChatMode.GROUP_CHAT
    )
    workspace_agent_key = "Multi-agent Workspaces"

    occam_agent = OccamAgent(
        name="occam-agent",
        client=occam_client,
        agent_name=workspace_agent_key,
        agent_params=agent_params,
    )

    other_agent = ConversableAgent(name="other-agent", llm_config={"model": "gpt-4o-mini", "api_type": "openai"})
    other_agent.initiate_chat(
        recipient=occam_agent,
        message="Hello, Start a chat about a random scientific topic.",
        max_turns=2,
    )
