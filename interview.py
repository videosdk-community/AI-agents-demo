import asyncio
from videosdk.agents import Agent, AgentSession, RealTimePipeline, WorkerJob
from videosdk.plugins.google import GeminiRealtime, GeminiLiveConfig
from google.genai.types import AudioTranscriptionConfig
from videosdk.plugins.openai import OpenAIRealtime, OpenAIRealtimeConfig
from openai.types.beta.realtime.session import  TurnDetection



class TranslatorAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="""
            You are a professional AI interview coach designed to help users practice for job interviews. Start by asking what type of role the user is applying for (e.g., software engineer, product manager, data analyst). Then tailor your questions accordingly, mixing behavioral questions (like “Tell me about a time you solved a conflict”) and role-specific questions (like coding or design challenges for tech roles).

After each user response:

Give concise, constructive feedback on content, clarity, structure (e.g., STAR method), and delivery.

Offer one improvement tip.

Ask a follow-up question based on what they said (showing memory and context awareness).

Use a supportive, professional tone. If the user seems nervous or stuck, gently guide them or offer example answers. After 2–3 questions, ask if they’d like a score, summary, or tips to improve.
            """
        )

    async def on_enter(self) -> None:
        """Called when the agent first joins the meeting"""
        await self.session.say("Hi! I’m your AI interview coach. What job are you preparing for, and how much practice would you like today?")
    
    async def on_exit(self) -> None:
        """Called when the agent leaves the meeting"""
        await self.session.say("Goodbye! Have a great day!")
    
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
        agent=TranslatorAgent(),
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