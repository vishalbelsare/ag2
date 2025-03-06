```python
import asyncio
import websockets
import json
from typing import Any
from autogen import ConversableAgent, LLMConfig
from autogen.tools import tool

# Set up LLMConfig as a context manager for agent configuration
llm_config = LLMConfig({"config_list": [{"api_key": "your-api-key", "model": "gpt-4o-mini"}]})

# Define tools for the agents
@tool(description="Search Wikipedia for the given query.")
def search_wikipedia(query: str) -> str:
    return "Leonardo da Vinci was an Italian polymath."

@tool(description="Send the answer to the user.")
def send_answer(answer: str) -> str:
    return f"Answer sent: {answer}"

async def run_agents_and_process_events():
    with llm_config:
        alice = ConversableAgent(system_message="You are a helpful assistant.")
        bob = ConversableAgent(system_message="You are a fact-checker.")

    alice.add_tool(search_wikipedia)
    bob.add_tool(send_answer)

    response = await a_run(alice, bob, message="Who is Leonardo da Vinci?")

    return response

async def process_event_loop(response: AsyncRunResponseProtocol, websocket: websockets.WebSocketServerProtocol):
    async for event in response.events:
        if event.type == "input_request":
            await websocket.send(json.dumps({"type": "input_request", "prompt": event.prompt}))
            user_input = await websocket.recv()
            event.respond(InputResponseEvent(value=user_input))

        elif event.type == "output":
            await websocket.send(json.dumps({"type": "output", "value": event.value}))

        elif event.type == "agent_message":
            await websocket.send(json.dumps({"type": "agent_message", "message": event.message}))

            # create checkpoint and save checkpoint
            checkpoint: Checkpoint = event.get_checkpoint()
            checkpoint_json = checkpoint.model_dump_json()
            with Path("/tmp/checkpoint.json").open("w") as f:
                f.write(checkpoint_json)

        elif event.type == "system":
            await websocket.send(json.dumps({"type": "system", "value": event.value}))

        elif event.type == "error":
            await websocket.send(json.dumps({"type": "error", "error": event.error}))
            return # we'll continue from this point using checkpoint


async def create_new_run(websocket: websockets.WebSocketServerProtocol, path: str):
    response = await run_agents_and_process_events()
    await process_event_loop(response, websocket)

async def continue_checkpoint(websocket: websockets.WebSocketServerProtocol, path: str):
    with Path("/tmp/checkpoint.json").open() as f:
        checkpoint_json = f.read()
    checkpoint = Checkpoint.model_load_json(checkpoint_json)

    response = await checkpoint.a_continue()

    await process_event_loop(response, websocket)


async def main(handler):
    server = await websockets.serve(handler, "localhost", 8765)
    print("WebSocket server started on ws://localhost:8765")
    await server.wait_closed()

# run until error
asyncio.run(main(create_new_run))

# continue from error
asyncio.run(main(continue_checkpoint))


```
