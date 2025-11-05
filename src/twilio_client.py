"""
Twilio integration for voice calls
"""
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
from typing import Optional
from loguru import logger

from src.config import settings


class TwilioVoiceClient:
    """Manages Twilio voice calls"""

    def __init__(self):
        self.client = Client(
            settings.twilio_account_sid,
            settings.twilio_auth_token
        )
        self.from_number = settings.twilio_phone_number
        logger.info(f"Initialized Twilio client with number {self.from_number}")

    def make_call(
        self,
        to_number: str,
        webhook_url: str,
        status_callback_url: Optional[str] = None
    ) -> str:
        """
        Initiate an outbound call

        Args:
            to_number: Phone number to call
            webhook_url: URL for Twilio to request when call is answered
            status_callback_url: Optional URL for call status updates

        Returns:
            Call SID
        """
        try:
            call = self.client.calls.create(
                to=to_number,
                from_=self.from_number,
                url=webhook_url,
                status_callback=status_callback_url,
                status_callback_event=['initiated', 'ringing', 'answered', 'completed'],
                record=False,  # Set to True if you want to record calls (check legal requirements!)
                machine_detection='DetectMessageEnd',  # Detect answering machines
                timeout=30  # Ring timeout in seconds
            )

            logger.info(f"Call initiated: {call.sid} to {to_number}")
            return call.sid

        except Exception as e:
            logger.error(f"Error making call to {to_number}: {e}")
            raise

    def get_call_status(self, call_sid: str) -> dict:
        """Get status of a call"""
        try:
            call = self.client.calls(call_sid).fetch()
            return {
                'sid': call.sid,
                'status': call.status,
                'duration': call.duration,
                'start_time': call.start_time,
                'end_time': call.end_time,
                'answered_by': getattr(call, 'answered_by', None)
            }
        except Exception as e:
            logger.error(f"Error fetching call status for {call_sid}: {e}")
            raise

    def hangup_call(self, call_sid: str):
        """Hangup an active call"""
        try:
            self.client.calls(call_sid).update(status='completed')
            logger.info(f"Call {call_sid} hung up")
        except Exception as e:
            logger.error(f"Error hanging up call {call_sid}: {e}")
            raise


class TwiMLGenerator:
    """Generate TwiML responses for Twilio webhooks"""

    @staticmethod
    def generate_media_stream_connect(stream_url: str) -> str:
        """
        Generate TwiML to connect Media Stream for ElevenLabs

        Args:
            stream_url: WebSocket URL for media streaming

        Returns:
            TwiML XML string
        """
        from twilio.twiml.voice_response import Connect, Stream

        response = VoiceResponse()

        # Start Media Stream
        connect = Connect()
        stream = Stream(url=stream_url)
        connect.append(stream)
        response.append(connect)

        return str(response)

    @staticmethod
    def generate_greeting(greeting_text: str, gather_url: str) -> str:
        """
        Generate TwiML for greeting and gathering user input

        Args:
            greeting_text: Text to speak
            gather_url: URL to send gathered speech input

        Returns:
            TwiML XML string
        """
        response = VoiceResponse()

        # Speak greeting and gather response
        gather = Gather(
            input='speech',
            action=gather_url,
            method='POST',
            language=settings.default_language,
            speech_timeout='auto',  # Auto-detect end of speech
            timeout=5,  # Wait 5 seconds for user to start speaking
            profanity_filter=False
        )

        gather.say(
            greeting_text,
            voice='Polly.Vicki',  # German female voice
            language=settings.default_language
        )

        response.append(gather)

        # If no input received
        response.say(
            "Entschuldigung, ich habe Sie nicht verstanden. Auf Wiederhören.",
            voice='Polly.Vicki',
            language=settings.default_language
        )
        response.hangup()

        return str(response)

    @staticmethod
    def generate_response(ai_response: str, gather_url: str, is_final: bool = False) -> str:
        """
        Generate TwiML for AI response and gathering next input

        Args:
            ai_response: AI generated text to speak
            gather_url: URL to send gathered speech input
            is_final: If True, end call after speaking

        Returns:
            TwiML XML string
        """
        response = VoiceResponse()

        if is_final:
            # Final message - just speak and hang up
            response.say(
                ai_response,
                voice='Polly.Vicki',
                language=settings.default_language
            )
            response.hangup()
        else:
            # Speak response and gather next input
            gather = Gather(
                input='speech',
                action=gather_url,
                method='POST',
                language=settings.default_language,
                speech_timeout='auto',
                timeout=5,
                profanity_filter=False
            )

            gather.say(
                ai_response,
                voice='Polly.Vicki',
                language=settings.default_language
            )

            response.append(gather)

            # If no input received
            response.say(
                "Sind Sie noch da?",
                voice='Polly.Vicki',
                language=settings.default_language
            )

            # Give one more chance
            final_gather = Gather(
                input='speech',
                action=gather_url,
                method='POST',
                language=settings.default_language,
                speech_timeout='auto',
                timeout=5,
                profanity_filter=False
            )
            response.append(final_gather)

            # Still no response - end call
            response.say(
                "Ich verstehe. Auf Wiederhören!",
                voice='Polly.Vicki',
                language=settings.default_language
            )
            response.hangup()

        return str(response)

    @staticmethod
    def generate_answering_machine_response() -> str:
        """Generate TwiML for answering machine detection"""
        response = VoiceResponse()
        response.say(
            "Guten Tag, hier ist ein Anruf von " + settings.company_name +
            ". Wir haben eine interessante Karrieremöglichkeit für Sie. " +
            "Bitte rufen Sie uns zurück unter " + settings.contact_phone +
            ". Vielen Dank!",
            voice='Polly.Vicki',
            language=settings.default_language
        )
        response.hangup()
        return str(response)

    @staticmethod
    def generate_error_response() -> str:
        """Generate TwiML for error handling"""
        response = VoiceResponse()
        response.say(
            "Entschuldigung, es gab ein technisches Problem. " +
            "Bitte rufen Sie uns zurück unter " + settings.contact_phone + ". " +
            "Auf Wiederhören.",
            voice='Polly.Vicki',
            language=settings.default_language
        )
        response.hangup()
        return str(response)

    @staticmethod
    def generate_hangup() -> str:
        """Generate TwiML to hangup"""
        response = VoiceResponse()
        response.hangup()
        return str(response)


# Testing
if __name__ == "__main__":
    # Test TwiML generation
    print("Testing TwiML Generation:")
    print("=" * 50)

    greeting = TwiMLGenerator.generate_greeting(
        "Guten Tag, hier ist Sarah von Hörakustik GmbH. Haben Sie kurz Zeit?",
        "https://example.com/gather"
    )
    print("\nGreeting TwiML:")
    print(greeting)

    print("\n" + "=" * 50)

    response_twiml = TwiMLGenerator.generate_response(
        "Perfekt! Wir haben eine spannende Position für Sie.",
        "https://example.com/gather",
        is_final=False
    )
    print("\nResponse TwiML:")
    print(response_twiml)

    print("\n" + "=" * 50)

    final_twiml = TwiMLGenerator.generate_response(
        "Vielen Dank für das Gespräch. Wir melden uns bald bei Ihnen!",
        "https://example.com/gather",
        is_final=True
    )
    print("\nFinal Response TwiML:")
    print(final_twiml)
