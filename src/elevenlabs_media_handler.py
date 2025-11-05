"""
Twilio Media Streams <-> ElevenLabs Bridge
Handles bidirectional audio streaming between Twilio and ElevenLabs
"""
import asyncio
import json
import base64
from fastapi import WebSocket
from loguru import logger

from src.elevenlabs_client import ElevenLabsConversationalAI


class MediaStreamBridge:
    """Bridges Twilio Media Streams with ElevenLabs Conversational AI"""

    def __init__(self, agent_id: str, api_key: str):
        self.agent_id = agent_id
        self.api_key = api_key
        self.elevenlabs_client = None
        self.twilio_ws = None
        self.stream_sid = None
        self.is_active = True

    async def handle_twilio_stream(self, websocket: WebSocket):
        """Handle incoming Twilio Media Stream WebSocket"""
        await websocket.accept()
        self.twilio_ws = websocket

        logger.info("Twilio Media Stream connected")

        # Initialize ElevenLabs
        self.elevenlabs_client = ElevenLabsConversationalAI(self.agent_id, self.api_key)
        await self.elevenlabs_client.connect()

        # Start bidirectional streaming
        try:
            # Task for receiving from Twilio and sending to ElevenLabs
            twilio_to_eleven_task = asyncio.create_task(self._twilio_to_elevenlabs())

            # Task for receiving from ElevenLabs and sending to Twilio
            eleven_to_twilio_task = asyncio.create_task(self._elevenlabs_to_twilio())

            # Wait for both tasks
            await asyncio.gather(
                twilio_to_eleven_task,
                eleven_to_twilio_task,
                return_exceptions=True
            )

        except Exception as e:
            logger.error(f"Error in media stream bridge: {e}")

        finally:
            await self.cleanup()

    async def _twilio_to_elevenlabs(self):
        """Receive audio from Twilio, send to ElevenLabs"""
        try:
            while self.is_active:
                # Receive from Twilio
                message = await self.twilio_ws.receive_text()
                data = json.loads(message)

                event = data.get("event")

                if event == "connected":
                    logger.info("Twilio connected event received")

                elif event == "start":
                    self.stream_sid = data.get("start", {}).get("streamSid")
                    logger.info(f"Media stream started: {self.stream_sid}")

                elif event == "media":
                    # Get audio payload from Twilio (mulaw, base64)
                    payload = data.get("media", {}).get("payload")

                    if payload and self.elevenlabs_client:
                        # Decode mulaw audio
                        audio_mulaw = base64.b64decode(payload)

                        # Convert mulaw to PCM (ElevenLabs expects PCM)
                        # Note: This is simplified - production needs proper conversion
                        # For now, send as-is and ElevenLabs will handle

                        # Send to ElevenLabs
                        await self.elevenlabs_client.send_audio(audio_mulaw)

                elif event == "stop":
                    logger.info("Media stream stopped")
                    self.is_active = False
                    break

        except Exception as e:
            logger.error(f"Error in Twilio->ElevenLabs stream: {e}")
            self.is_active = False

    async def _elevenlabs_to_twilio(self):
        """Receive audio from ElevenLabs, send to Twilio"""
        try:
            while self.is_active and self.elevenlabs_client:
                # Receive audio from ElevenLabs
                audio_data = await self.elevenlabs_client.receive_audio()

                if audio_data == "DONE":
                    logger.info("Agent finished speaking")
                    continue

                elif audio_data == "INTERRUPT":
                    # Clear Twilio buffer
                    await self._send_clear_to_twilio()
                    continue

                elif audio_data and isinstance(audio_data, bytes):
                    # Send audio to Twilio
                    await self._send_audio_to_twilio(audio_data)

        except Exception as e:
            logger.error(f"Error in ElevenLabs->Twilio stream: {e}")
            self.is_active = False

    async def _send_audio_to_twilio(self, audio_bytes: bytes):
        """Send audio to Twilio Media Stream"""
        if not self.twilio_ws or not self.stream_sid:
            return

        try:
            # Convert PCM to mulaw (simplified - production needs proper conversion)
            audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')

            message = {
                "event": "media",
                "streamSid": self.stream_sid,
                "media": {
                    "payload": audio_b64
                }
            }

            await self.twilio_ws.send_text(json.dumps(message))

        except Exception as e:
            logger.error(f"Error sending audio to Twilio: {e}")

    async def _send_clear_to_twilio(self):
        """Clear Twilio playback buffer (for interruptions)"""
        if not self.twilio_ws or not self.stream_sid:
            return

        try:
            message = {
                "event": "clear",
                "streamSid": self.stream_sid
            }

            await self.twilio_ws.send_text(json.dumps(message))
            logger.info("Cleared Twilio buffer")

        except Exception as e:
            logger.error(f"Error clearing Twilio buffer: {e}")

    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up media stream bridge")

        self.is_active = False

        if self.elevenlabs_client:
            await self.elevenlabs_client.end_conversation()

        if self.twilio_ws:
            try:
                await self.twilio_ws.close()
            except:
                pass
