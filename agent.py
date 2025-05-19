from videosdk.agents import Agent, function_tool
import aiohttp
import asyncio
from videosdk.plugins.openai import OpenAIRealtime, OpenAIRealtimeConfig
from videosdk.agents import RealTimePipeline
from openai.types.beta.realtime.session import TurnDetection
from videosdk.agents import AgentSession, WorkerJob

@function_tool
async def get_weather(latitude: str, longitude: str):
    """Called when the user asks about the weather. This function will return the weather for
    the given location. When given a location, please estimate the latitude and longitude of the
    location and do not ask the user for them.

    Args:
        latitude: The latitude of the location
        longitude: The longitude of the location
    """
    print(f"Getting weather for {latitude}, {longitude}")
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    "temperature": data["current"]["temperature_2m"],
                    "temperature_unit": "Celsius",
                }
            else:
                raise Exception(
                    f"Failed to get weather data, status code: {response.status}"
                )

class VoiceAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="You are a helpful voice assistant that can answer questions and help with tasks.",
             tools=[get_weather] # You can register any external tool defined outside of this scope
        )

    async def on_enter(self) -> None:
        """Called when the agent first joins the meeting"""
        await self.session.say("Hi there! How can I help you today?")
    
    async def on_exit(self) -> None:
        """Called when the agent leaves the meeting"""
        await self.session.say("Goodbye! Have a great day!")
    
    @function_tool
    async def get_horoscope(self, sign: str) -> dict:
        """Get today's horoscope for a given zodiac sign.

        Args:
            sign: The zodiac sign (e.g., Aries, Taurus, Gemini, etc.)
        """
        horoscopes = {
            "Aries": "Today is your lucky day!",
            "Taurus": "Focus on your goals today.",
            "Gemini": "Communication will be important today.",
        }
        return {
            "sign": sign,
            "horoscope": horoscopes.get(sign, "The stars are aligned for you today!"),
        }
async def start_session(jobctx):
    # Initialize the AI model
    model = OpenAIRealtime(
        model="gpt-4o-realtime-preview",
        config=OpenAIRealtimeConfig(
            modalities=["text", "audio"],
            turn_detection=TurnDetection(
                type="server_vad",
                threshold=0.5,
                prefix_padding_ms=300,
                silence_duration_ms=200,
            ),
            tool_choice="auto"
        )
    )

    pipeline = RealTimePipeline(model=model)

    # Create the agent session
    session = AgentSession(
        agent=VoiceAgent(),
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
            "meetingId": "061i-7jyc-7ztt",  # Use the generated meeting ID from earlier
            "name": "AI Assistant",   # Name displayed in the meeting
        }

    # Create and start the worker job
    job = WorkerJob(job_func=entryPoint, jobctx=make_context)
    job.start()