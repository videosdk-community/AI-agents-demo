from videosdk.agents import Agent, function_tool
import aiohttp
import asyncio
from videosdk.plugins.openai import OpenAIRealtime, OpenAIRealtimeConfig
from videosdk.agents import RealTimePipeline
from openai.types.beta.realtime.session import TurnDetection
from videosdk.agents import AgentSession, WorkerJob
import os
from openai import OpenAI


class MedicalTriageAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions=
                """
sfkhfkd
    """,
        )

    async def on_enter(self) -> None:
        """Called when the agent first joins the meeting."""
        await self.session.say("Hello! I'm your medical services assistant. Are you looking for billing help, medical support, or something else today?")

    async def on_exit(self) -> None:
        """Called when the agent leaves the meeting."""
        await self.session.say("Thank you for using our services. Goodbye!")

    @function_tool
    async def billing(self, user_query: str):
        """
        Call this function if the user's query is primarily about billing, invoices, payments, charges, or other financial matters.
        Pass the user's full query to this function.

        Args:
            user_query: The user's full original query related to billing.
        """
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        client = OpenAI() # Local client as per original user code
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="gpt-4.1-2025-04-14",
            messages=[
                {"role": "system", "content": """
You are the Medical Billing agent at a healthcare office. You help patients with insurance information,
    """ },
            {"role": "user", "content": user_query},
        ],
        temperature=0.7,
    )

        billing_response_content = response.choices[0].message.content
        print(f"Billing tool (internal LLM) response: {billing_response_content}")
        # Return a dictionary, so the main Triage LLM knows what this info is.
        return {"status": "success", "billing_response": billing_response_content.strip()}



 

# --- Session Setup and Entry Point ---

async def start_session(jobctx):
    # Initialize the AI models
    model = OpenAIRealtime(
    model="gpt-4o-realtime-preview",
    config=OpenAIRealtimeConfig(
        modalities=["text", "audio"],
        turn_detection=TurnDetection(
            type="server_vad",
            threshold=0.5,
            prefix_padding_ms=300,
            silence_duration_ms=200,
        )
    )
)
#     model = GeminiRealtime(
#     model="gemini-2.5-flash-exp-native-audio-thinking-dialog",
#     api_key="AIzaSyARnYlVzgb73R_5RSjq1oYu52R-Y4TE7TY",  # Or use environment variable
#     config=GeminiLiveConfig(
#         response_modalities=["AUDIO"]
#     )
# )

    pipeline = RealTimePipeline(model=model)

    # Create the agent session
    session = AgentSession(
        agent=MedicalTriageAgent(),
        pipeline=pipeline,
        context=jobctx
    )

    try:
        # Start the session
        await session.start()
        # Keep the session running until manually terminated
        await asyncio.Event().wait()
    finally:
        # Clean up resources when done
        await session.close()

def entryPoint(jobctx):
    asyncio.run(start_session(jobctx))

if __name__ == "__main__":
    def make_context():
        return {
            "meetingId": "nrn8-5lb2-zadr",  # Use the generated meeting ID from earlier
            "name": "VideoSDK's AI Agent",   # Name displayed in the meeting
        }

    # Create and start the worker job
    job = WorkerJob(job_func=entryPoint, jobctx=make_context)
    job.start()