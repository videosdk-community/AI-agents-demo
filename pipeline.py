from videosdk.agents import RealTimePipeline
from videosdk.plugins.openai import OpenAIRealtime, OpenAIRealtimeConfig
from openai.types.beta.realtime.session import TurnDetection


def create_pipeline():
    """Initializes and returns the RealTimePipeline with OpenAI realtime model"""
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
    pipeline = RealTimePipeline(model=model)
    return pipeline