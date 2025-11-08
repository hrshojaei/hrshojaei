"""
ElevenLabs Conversational AI Integration
Real-time voice conversation with low latency
"""
import asyncio
import json
import base64
from typing import Optional
import websockets
from loguru import logger

from src.config import settings


class ElevenLabsConversationalAI:
    """Manages ElevenLabs Conversational AI for real-time voice calls"""

    def __init__(self, agent_id: str, api_key: Optional[str] = None):
        self.agent_id = agent_id
        self.api_key = api_key or settings.elevenlabs_api_key
        self.websocket = None
        self.conversation_id = None

        # ElevenLabs WebSocket endpoint
        self.ws_url = f"wss://api.elevenlabs.io/v1/convai/conversation?agent_id={self.agent_id}"

        logger.info(f"Initialized ElevenLabs Conversational AI with agent {agent_id}")

    async def connect(self):
        """Connect to ElevenLabs WebSocket"""
        try:
            headers = {
                "xi-api-key": self.api_key
            }

            self.websocket = await websockets.connect(
                self.ws_url,
                extra_headers=headers
            )

            logger.info("Connected to ElevenLabs WebSocket")

            # Wait for conversation_initiation_metadata
            init_message = await self.websocket.recv()
            init_data = json.loads(init_message)

            if init_data.get("type") == "conversation_initiation_metadata":
                self.conversation_id = init_data.get("conversation_initiation_metadata_event", {}).get("conversation_id")
                logger.info(f"Conversation started: {self.conversation_id}")

            return True

        except Exception as e:
            logger.error(f"Failed to connect to ElevenLabs: {e}")
            return False

    async def send_audio(self, audio_chunk: bytes):
        """Send audio chunk to ElevenLabs"""
        if not self.websocket:
            logger.error("WebSocket not connected")
            return

        try:
            # Convert audio to base64
            audio_b64 = base64.b64encode(audio_chunk).decode('utf-8')

            message = {
                "user_audio_chunk": audio_b64
            }

            await self.websocket.send(json.dumps(message))

        except Exception as e:
            logger.error(f"Error sending audio to ElevenLabs: {e}")

    async def receive_audio(self):
        """Receive audio response from ElevenLabs"""
        if not self.websocket:
            logger.error("WebSocket not connected")
            return None

        try:
            while True:
                message = await self.websocket.recv()
                data = json.loads(message)

                msg_type = data.get("type")

                # DEBUG: Log all message types to see what ElevenLabs sends
                logger.debug(f"ElevenLabs message type: {msg_type}")

                if msg_type == "audio":
                    # Agent speaking
                    audio_b64 = data.get("audio_event", {}).get("audio_base_64")
                    if audio_b64:
                        audio_bytes = base64.b64decode(audio_b64)
                        logger.debug(f"Received audio chunk: {len(audio_bytes)} bytes")
                        return audio_bytes
                    else:
                        logger.warning(f"Audio message without data: {data}")

                elif msg_type == "interruption":
                    logger.info("User interrupted agent")
                    return "INTERRUPT"

                elif msg_type == "agent_response":
                    logger.info("Agent finished speaking")
                    return "DONE"

                elif msg_type == "user_transcript":
                    transcript = data.get("user_transcription_event", {}).get("user_transcript")
                    logger.info(f"User said: {transcript}")

                elif msg_type == "internal_tentative_agent_response":
                    # Agent is thinking
                    pass

        except Exception as e:
            logger.error(f"Error receiving from ElevenLabs: {e}")
            return None

    async def end_conversation(self):
        """End the conversation"""
        if self.websocket:
            try:
                await self.websocket.close()
                logger.info("ElevenLabs conversation ended")
            except Exception as e:
                logger.error(f"Error closing WebSocket: {e}")

    def get_conversation_config(self) -> dict:
        """Get conversation configuration for client"""
        return {
            "agent_id": self.agent_id,
            "conversation_id": self.conversation_id,
            "websocket_url": self.ws_url
        }


async def test_elevenlabs():
    """Test ElevenLabs connection"""
    agent_id = "agent_2101k99zvybyf6ftnthftr6z454r"
    api_key = "sk_a979e7e06a857f728a392f995f3ec85e448b2ce9260f65f8"

    client = ElevenLabsConversationalAI(agent_id, api_key)

    connected = await client.connect()
    if connected:
        print("✅ Successfully connected to ElevenLabs!")
        print(f"Conversation ID: {client.conversation_id}")

        await client.end_conversation()
    else:
        print("❌ Failed to connect to ElevenLabs")


if __name__ == "__main__":
    asyncio.run(test_elevenlabs())
