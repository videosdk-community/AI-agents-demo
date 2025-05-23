import asyncio
from videosdk.agents import AgentSession, WorkerJob
from agent import VoiceAgent
from pipeline import create_pipeline
import logging

logging.basicConfig(level=logging.INFO)

async def start_session(jobctx):
    # Create the pipeline using the helper function
    pipeline = create_pipeline()

    # Create the agent session
    session = AgentSession(
        agent=VoiceAgent(),
        pipeline=pipeline,
        context=jobctx
    )

    try:
        logging.info("Starting VoiceAgent session...")
        # Start the session
        await session.start()
        # Keep the session running until manually terminated
        await asyncio.Event().wait()
    finally:
        # Clean up resources when done
        logging.info("Closing VoiceAgent session...")
        await session.close()


def entryPoint(jobctx):
    asyncio.run(start_session(jobctx))


if __name__ == "__main__":
    def make_context():
        return {
            "meetingId": "4mch-akup-kssd",  # Use the generated meeting ID from earlier
            "name": "VideoSDK's AI Agent",   # Name displayed in the meeting
        }

    # Create and start the worker job
    job = WorkerJob(job_func=entryPoint, jobctx=make_context())
    job.start()
