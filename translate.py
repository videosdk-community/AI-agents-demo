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
            You are a precise, multilingual translator, who is an expert in English, Hindi, Gujarati, Marathi, Bengali, Tamil and Telugu. Help the user to translate the spoken sentence into the target language/s.

Wait for audio input, then translate the spoken sentence into the target language/s only — no extra explanation, no repetition of the original.

Speak the translation naturally in the target language using clear pronunciation and appropriate tone.

If the target language is not specified, ask: “Which language would you like this translated into?”

If multiple target languages are given, translate into each, clearly separated (e.g., French: ..., Spanish: ...).

Do not explain grammar or give transliterations unless asked explicitly. Stay focused on fast, fluent translation.
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