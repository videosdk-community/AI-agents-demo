# VideoSDK AI Agent Voice Assistant

This project implements a multi-agent voice assistant using [VideoSDK Agents](https://docs.videosdk.live/agents/overview) and `videosdk-plugins-openai`. It enables real-time conversational AI agents that can join meetings, respond using voice, and be customized using structured prompting logic.

## Features

- Multi-agent support (e.g., triage, billing, support personas)
- Real-time speech synthesis and response using OpenAI GPT-4o
- Modular prompting logic using `prompts.py` and `prompting.py`
- Designed for voice-based applications in domains like medical triage

## Project Structure

- `prompting.py`: Logic for dynamically constructing prompts using context.
- `prompts.py`: Static or templated prompt definitions per agent or use case.
- `requirements.txt`: Lists the required dependencies to run this system.

## Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

## Getting Started

1. **Set up VideoSDK and OpenAI credentials** in your environment as per [VideoSDK docs](https://docs.videosdk.live/agents/overview).

2. **Run your agent** using an entry script like the following:

```python
from videosdk.agents import AgentSession
from prompting import generate_prompt  # example
from prompts import TRIAGE_PROMPT  # example

session = AgentSession(agent_name="TriageAgent")

@session.on_call_start
def on_start(call):
    prompt = generate_prompt(call.context)
    call.say(prompt)

session.run_forever()
```

3. **Define prompt behaviors** in `prompts.py` and implement logic to adjust responses in `prompting.py`.

## Customization

- Add new personas by defining prompts and prompt templates in `prompts.py`.
- Use logic in `prompting.py` to construct intelligent responses or context-aware prompts.
- Plug in tools, APIs, or memory functions via `function_call` decorators.
