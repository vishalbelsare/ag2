import os
from autogen.agentchat.conversable_agent import ConversableAgent
from autogen.agents.experimental.occam.occam import OccamAgent


if __name__ == "__main__":
    # TODO: Select agent from catalogue
    ...

    # TODO: Populate necessary instance params
    ...
    # agent_params = ...

    api_key = os.getenv("OCCAM_API_KEY")
    base_url = os.getenv("OCCAM_BASE_URL", "https://api.occam.ai")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    occam_agent = OccamAgent(
        api_key=api_key,
        base_url=base_url,
        name="occam-agent",
    )

    other_agent = ConversableAgent(name="other-agent", llm_config={"model": "gpt-4o-mini", "api_type": "openai"})
    other_agent.initiate_chat(
        recipient=occam_agent, message="Hello, tell me an interesting fact about the moon.", max_turns=2
    )
