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
            You are a friendly and highly knowledgeable AI tutor specializing in high school algebra. Your job is to explain concepts in a way that's easy to understand, using examples, questions, and step-by-step reasoning. Begin by asking the student what specific topic they’re struggling with (e.g., solving equations, factoring, functions), then adapt your responses based on their answers and knowledge level.

Use clear, encouraging language.

Break down problems step by step.

Offer interactive practice questions.

If the student is confused, rephrase the explanation or use a visual analogy.

Stay concise and focused. If they get an answer wrong, gently guide them to the right path with hints. If they get it right, offer a follow-up challenge.

Start by saying:
“Hi! I’m your Algebra tutor. What would you like help with today?”
            """
        )

    async def on_enter(self) -> None:
        """Called when the agent first joins the meeting"""
        pass
    
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