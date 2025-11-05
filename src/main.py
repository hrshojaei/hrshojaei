"""
Main application - FastAPI server and CLI interface
"""
import sys
from fastapi import FastAPI, Form, Request, Response, WebSocket
from fastapi.responses import PlainTextResponse
import uvicorn
from loguru import logger
from typing import Optional
import asyncio

from src.config import settings
from src.candidate_manager import CandidateManager
from src.twilio_client import TwilioVoiceClient, TwiMLGenerator
from src.call_handler import call_handler


# Configure logging
logger.remove()  # Remove default handler
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=settings.log_level
)

if settings.log_to_file:
    logger.add(
        "./logs/calling_agent_{time}.log",
        rotation="1 day",
        retention="30 days",
        level=settings.log_level
    )

# Initialize FastAPI app
app = FastAPI(
    title="AI Recruiting Call Agent",
    description="Automated recruitment calls for Hörakustik industry",
    version="1.0.0"
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "AI Recruiting Call Agent",
        "version": "1.0.0"
    }


@app.post("/webhook/call/start", response_class=PlainTextResponse)
async def webhook_call_start(
    request: Request,
    CallSid: str = Form(...),
    From: Optional[str] = Form(None),
    To: Optional[str] = Form(None)
):
    """
    Webhook called when call is initiated by Twilio
    Expected to be called with candidate_id in URL params
    """
    logger.info(f"Call start webhook: {CallSid}")

    # Get candidate_id from query params
    candidate_id = request.query_params.get('candidate_id')
    if not candidate_id:
        logger.error("No candidate_id provided in webhook")
        return TwiMLGenerator.generate_error_response()

    try:
        candidate_id = int(candidate_id)

        # Build gather URL for this call
        gather_url = f"{settings.public_url}/webhook/call/gather?call_sid={CallSid}"

        # Handle call start
        twiml = await call_handler.handle_call_start(
            call_sid=CallSid,
            candidate_id=candidate_id,
            gather_url=gather_url
        )

        return Response(content=twiml, media_type="application/xml")

    except Exception as e:
        logger.error(f"Error in call start webhook: {e}")
        from src.twilio_client import TwiMLGenerator
        return Response(
            content=TwiMLGenerator.generate_error_response(),
            media_type="application/xml"
        )


@app.post("/webhook/call/gather", response_class=PlainTextResponse)
async def webhook_call_gather(
    request: Request,
    CallSid: str = Form(...),
    SpeechResult: Optional[str] = Form(None),
    AnsweredBy: Optional[str] = Form(None)
):
    """
    Webhook called when user speech is gathered
    """
    logger.info(f"Call gather webhook: {CallSid}, speech: {SpeechResult}")

    try:
        # Build gather URL for next turn
        gather_url = f"{settings.public_url}/webhook/call/gather?call_sid={CallSid}"

        # Handle user speech
        twiml = await call_handler.handle_user_speech(
            call_sid=CallSid,
            user_speech=SpeechResult or "",
            gather_url=gather_url,
            answered_by=AnsweredBy
        )

        return Response(content=twiml, media_type="application/xml")

    except Exception as e:
        logger.error(f"Error in call gather webhook: {e}")
        from src.twilio_client import TwiMLGenerator
        return Response(
            content=TwiMLGenerator.generate_error_response(),
            media_type="application/xml"
        )


@app.post("/webhook/call/status")
async def webhook_call_status(
    CallSid: str = Form(...),
    CallStatus: str = Form(...),
    CallDuration: Optional[int] = Form(None)
):
    """
    Webhook called for call status updates
    """
    logger.info(f"Call status webhook: {CallSid}, status: {CallStatus}, duration: {CallDuration}")

    try:
        await call_handler.handle_call_status(
            call_sid=CallSid,
            call_status=CallStatus,
            call_duration=CallDuration
        )
        return {"status": "ok"}

    except Exception as e:
        logger.error(f"Error in call status webhook: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/stats")
async def get_statistics():
    """Get calling statistics"""
    manager = CandidateManager()
    stats = manager.get_statistics()
    return stats


# ElevenLabs Conversational AI Endpoints
@app.websocket("/ws/media-stream/{call_sid}")
async def websocket_media_stream(websocket: WebSocket, call_sid: str):
    """Handle Twilio Media Stream WebSocket for ElevenLabs"""
    from src.elevenlabs_media_handler import MediaStreamBridge

    logger.info(f"Media Stream WebSocket connected for call {call_sid}")

    bridge = MediaStreamBridge(
        agent_id=settings.elevenlabs_agent_id,
        api_key=settings.elevenlabs_api_key
    )

    await bridge.handle_twilio_stream(websocket)


@app.post("/webhook/call/start-elevenlabs", response_class=PlainTextResponse)
async def webhook_call_start_elevenlabs(
    request: Request,
    CallSid: str = Form(...),
    From: Optional[str] = Form(None),
    To: Optional[str] = Form(None)
):
    """
    Webhook for ElevenLabs Conversational AI calls
    Uses Twilio Media Streams instead of Gather
    """
    logger.info(f"ElevenLabs call start: {CallSid}")

    # Build WebSocket URL for Media Streams
    # Replace http:// with ws:// or https:// with wss://
    ws_url = settings.public_url.replace("http://", "ws://").replace("https://", "wss://")
    stream_url = f"{ws_url}/ws/media-stream/{CallSid}"

    logger.info(f"Connecting to ElevenLabs via Media Stream: {stream_url}")

    # Generate TwiML to connect Media Stream
    twiml = TwiMLGenerator.generate_media_stream_connect(stream_url)

    return Response(content=twiml, media_type="application/xml")


# CLI Functions
def start_server():
    """Start the FastAPI server"""
    logger.info(f"Starting server on {settings.server_host}:{settings.server_port}")
    logger.info(f"Public URL: {settings.public_url}")
    logger.info(f"AI Provider: {settings.ai_provider}")

    uvicorn.run(
        "src.main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=False,
        log_level=settings.log_level.lower()
    )


def make_test_call(phone: str):
    """Make a test call to a phone number"""
    logger.info(f"Making test call to {phone}")

    # Find or create candidate
    manager = CandidateManager()
    candidate = manager.get_candidate(phone=phone)

    if not candidate:
        logger.info(f"Creating new test candidate for {phone}")
        candidate_id = manager.add_candidate(
            name="Test Candidate",
            phone=phone,
            notes="Test call"
        )
    else:
        candidate_id = candidate.id

    # Make call
    twilio_client = TwilioVoiceClient()

    # Use ElevenLabs webhook if enabled
    if settings.use_elevenlabs_conversational:
        webhook_url = f"{settings.public_url}/webhook/call/start-elevenlabs"
        logger.info("Using ElevenLabs Conversational AI")
    else:
        webhook_url = f"{settings.public_url}/webhook/call/start?candidate_id={candidate_id}"
        logger.info("Using traditional OpenAI flow")

    status_callback_url = f"{settings.public_url}/webhook/call/status"

    try:
        call_sid = twilio_client.make_call(
            to_number=phone,
            webhook_url=webhook_url,
            status_callback_url=status_callback_url
        )
        logger.info(f"✓ Call initiated: {call_sid}")
        print(f"\n✓ Call initiated successfully!")
        print(f"Call SID: {call_sid}")
        print(f"Candidate ID: {candidate_id}")
        print(f"\nMonitor the call at: https://console.twilio.com/")

    except Exception as e:
        logger.error(f"Failed to make call: {e}")
        print(f"\n✗ Failed to make call: {e}")


def start_campaign(max_calls: int = 10):
    """Start calling campaign"""
    logger.info(f"Starting campaign with max {max_calls} calls")
    print(f"\n🚀 Starting calling campaign (max {max_calls} calls)...")

    manager = CandidateManager()
    candidates = manager.get_candidates_to_call(limit=max_calls)

    if not candidates:
        print("\n✓ No candidates to call!")
        return

    print(f"\nFound {len(candidates)} candidates to call:")
    for i, candidate in enumerate(candidates, 1):
        print(f"  {i}. {candidate.name} - {candidate.phone} ({candidate.status})")

    print("\n")
    confirm = input("Continue with calls? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Campaign cancelled.")
        return

    # Make calls with delay between each
    twilio_client = TwilioVoiceClient()
    successful_calls = 0

    for candidate in candidates:
        try:
            print(f"\nCalling {candidate.name} ({candidate.phone})...")

            # Use ElevenLabs webhook if enabled
            if settings.use_elevenlabs_conversational:
                webhook_url = f"{settings.public_url}/webhook/call/start-elevenlabs"
            else:
                webhook_url = f"{settings.public_url}/webhook/call/start?candidate_id={candidate.id}"

            status_callback_url = f"{settings.public_url}/webhook/call/status"

            call_sid = twilio_client.make_call(
                to_number=candidate.phone,
                webhook_url=webhook_url,
                status_callback_url=status_callback_url
            )

            print(f"  ✓ Call initiated: {call_sid}")
            successful_calls += 1

            # Wait before next call (to avoid rate limits)
            import time
            time.sleep(2)

        except Exception as e:
            print(f"  ✗ Failed: {e}")
            logger.error(f"Failed to call {candidate.phone}: {e}")

    print(f"\n✓ Campaign completed!")
    print(f"Successful calls: {successful_calls}/{len(candidates)}")


def show_statistics():
    """Show calling statistics"""
    manager = CandidateManager()
    stats = manager.get_statistics()

    print("\n📊 Calling Agent Statistics")
    print("=" * 50)
    print(f"\nTotal Candidates: {stats['total_candidates']}")
    print(f"Total Calls: {stats['total_calls']}")
    print(f"Average Call Duration: {stats['avg_call_duration_seconds']} seconds")

    print("\nCandidates by Status:")
    for status, count in stats.get('by_status', {}).items():
        print(f"  {status}: {count}")

    print("\n")


def add_candidate_cli():
    """Interactive CLI to add a candidate"""
    print("\n➕ Add New Candidate")
    print("=" * 50)

    name = input("Name: ")
    phone = input("Phone (with country code, e.g., +4915112345678): ")
    email = input("Email (optional): ") or None
    current_company = input("Current Company (optional): ") or None
    current_position = input("Current Position (optional): ") or None
    experience_years = input("Years of Experience (optional): ")
    experience_years = int(experience_years) if experience_years else None
    notes = input("Notes (optional): ") or None

    manager = CandidateManager()
    try:
        candidate_id = manager.add_candidate(
            name=name,
            phone=phone,
            email=email,
            current_company=current_company,
            current_position=current_position,
            experience_years=experience_years,
            notes=notes
        )
        print(f"\n✓ Candidate added successfully! ID: {candidate_id}")

    except Exception as e:
        print(f"\n✗ Error adding candidate: {e}")


def main():
    """Main CLI entry point"""
    if len(sys.argv) < 2:
        print("""
AI Recruiting Call Agent - CLI

Usage:
    python -m src.main server                 - Start the webhook server
    python -m src.main call <phone>           - Make a test call
    python -m src.main campaign [max_calls]   - Start calling campaign
    python -m src.main add                    - Add a candidate
    python -m src.main stats                  - Show statistics

Examples:
    python -m src.main server
    python -m src.main call +4915112345678
    python -m src.main campaign 10
    python -m src.main add
    python -m src.main stats
        """)
        return

    command = sys.argv[1]

    if command == "server":
        start_server()

    elif command == "call":
        if len(sys.argv) < 3:
            print("Error: Please provide phone number")
            print("Usage: python -m src.main call <phone>")
            return
        phone = sys.argv[2]
        make_test_call(phone)

    elif command == "campaign":
        max_calls = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        start_campaign(max_calls)

    elif command == "add":
        add_candidate_cli()

    elif command == "stats":
        show_statistics()

    else:
        print(f"Unknown command: {command}")
        print("Run 'python -m src.main' for usage help")


if __name__ == "__main__":
    main()
