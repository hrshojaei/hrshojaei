"""
Call handler - Orchestrates the conversation flow
"""
from typing import Dict, Optional
from datetime import datetime
from loguru import logger

from src.ai_engine import AIConversationEngine
from src.candidate_manager import CandidateManager, CandidateStatus
from src.twilio_client import TwiMLGenerator
from src.prompts import get_greeting_template


class CallSession:
    """Represents an active call session"""

    def __init__(self, call_sid: str, candidate_id: int, candidate_data: dict):
        self.call_sid = call_sid
        self.candidate_id = candidate_id
        self.candidate_data = candidate_data
        self.ai_engine = AIConversationEngine()
        self.turn_count = 0
        self.started_at = datetime.now()
        self.is_greeting_sent = False

        # Initialize AI conversation
        self.ai_engine.initialize_conversation(candidate_data)

        logger.info(f"Created call session {call_sid} for candidate {candidate_id}")

    def increment_turn(self):
        """Increment conversation turn counter"""
        self.turn_count += 1

    def should_end_call(self) -> bool:
        """Determine if call should end based on turn count"""
        from src.config import settings
        return self.turn_count >= settings.max_conversation_turns

    def get_duration_seconds(self) -> int:
        """Get call duration in seconds"""
        return int((datetime.now() - self.started_at).total_seconds())


class CallHandler:
    """Handles call flow and manages active sessions"""

    def __init__(self):
        self.active_sessions: Dict[str, CallSession] = {}
        self.candidate_manager = CandidateManager()
        logger.info("CallHandler initialized")

    def start_call_session(self, call_sid: str, candidate_id: int) -> CallSession:
        """Start a new call session"""
        # Get candidate data
        candidate = self.candidate_manager.get_candidate(candidate_id=candidate_id)
        if not candidate:
            raise ValueError(f"Candidate {candidate_id} not found")

        candidate_data = candidate.to_dict()

        # Create session
        session = CallSession(call_sid, candidate_id, candidate_data)
        self.active_sessions[call_sid] = session

        # Create call log in database
        call_log_id = self.candidate_manager.create_call_log(
            candidate_id=candidate_id,
            call_sid=call_sid
        )
        session.call_log_id = call_log_id

        # Update candidate status
        self.candidate_manager.update_candidate_status(
            candidate_id,
            CandidateStatus.CONTACTED
        )
        self.candidate_manager.update_last_contact(candidate_id)

        logger.info(f"Started call session for candidate {candidate_id}")
        return session

    def get_session(self, call_sid: str) -> Optional[CallSession]:
        """Get active session by call SID"""
        return self.active_sessions.get(call_sid)

    async def handle_call_start(self, call_sid: str, candidate_id: int, gather_url: str) -> str:
        """
        Handle call start - generate greeting TwiML

        Args:
            call_sid: Twilio call SID
            candidate_id: Candidate ID
            gather_url: URL for gathering user speech

        Returns:
            TwiML response
        """
        try:
            # Start session
            session = self.start_call_session(call_sid, candidate_id)

            # Generate personalized greeting
            candidate_name = session.candidate_data.get('name', '').split()[-1] if session.candidate_data.get('name') else ''
            greeting = get_greeting_template(candidate_name)

            # Log greeting
            self.candidate_manager.add_conversation_message(
                session.call_log_id,
                role="assistant",
                message=greeting
            )

            session.is_greeting_sent = True

            # Generate TwiML
            return TwiMLGenerator.generate_greeting(greeting, gather_url)

        except Exception as e:
            logger.error(f"Error handling call start: {e}")
            return TwiMLGenerator.generate_error_response()

    async def handle_user_speech(
        self,
        call_sid: str,
        user_speech: str,
        gather_url: str,
        answered_by: Optional[str] = None
    ) -> str:
        """
        Handle user speech input

        Args:
            call_sid: Twilio call SID
            user_speech: Transcribed user speech
            gather_url: URL for next gather
            answered_by: Machine detection result (human/machine)

        Returns:
            TwiML response
        """
        try:
            # Check for answering machine
            if answered_by and 'machine' in answered_by.lower():
                logger.info(f"Answering machine detected for call {call_sid}")
                return TwiMLGenerator.generate_answering_machine_response()

            # Get session
            session = self.get_session(call_sid)
            if not session:
                logger.error(f"No session found for call {call_sid}")
                return TwiMLGenerator.generate_error_response()

            # Log user speech
            self.candidate_manager.add_conversation_message(
                session.call_log_id,
                role="user",
                message=user_speech
            )

            logger.info(f"User speech [{call_sid}]: {user_speech}")

            # Detect if user wants to end call
            if self._is_goodbye(user_speech):
                logger.info(f"User wants to end call {call_sid}")
                goodbye_msg = "Vielen Dank für Ihre Zeit. Auf Wiederhören!"
                self.candidate_manager.add_conversation_message(
                    session.call_log_id,
                    role="assistant",
                    message=goodbye_msg
                )
                await self._end_call_session(call_sid, outcome="user_ended")
                return TwiMLGenerator.generate_response(goodbye_msg, gather_url, is_final=True)

            # Get AI response
            ai_response = await session.ai_engine.get_response(user_speech)

            # Log AI response
            self.candidate_manager.add_conversation_message(
                session.call_log_id,
                role="assistant",
                message=ai_response
            )

            logger.info(f"AI response [{call_sid}]: {ai_response}")

            # Increment turn
            session.increment_turn()

            # Check if should end call
            is_final = session.should_end_call()
            if is_final:
                logger.info(f"Max turns reached for call {call_sid}, ending call")
                await self._end_call_session(call_sid, outcome="max_turns_reached")

            # Detect if AI wants to end call (contains goodbye phrases)
            if self._is_ai_goodbye(ai_response):
                logger.info(f"AI ending call {call_sid}")
                is_final = True
                await self._end_call_session(call_sid, outcome="natural_end")

            # Generate TwiML response
            return TwiMLGenerator.generate_response(ai_response, gather_url, is_final=is_final)

        except Exception as e:
            logger.error(f"Error handling user speech: {e}")
            return TwiMLGenerator.generate_error_response()

    async def handle_call_status(self, call_sid: str, call_status: str, call_duration: Optional[int] = None):
        """
        Handle call status updates from Twilio

        Args:
            call_sid: Twilio call SID
            call_status: Call status (initiated, ringing, in-progress, completed, etc.)
            call_duration: Call duration in seconds
        """
        logger.info(f"Call status update [{call_sid}]: {call_status}, duration: {call_duration}")

        session = self.get_session(call_sid)

        if call_status == 'completed' and session:
            # Call ended
            await self._end_call_session(call_sid, outcome="completed", duration=call_duration)

        elif call_status == 'no-answer' or call_status == 'busy' or call_status == 'failed':
            # Call failed
            if session:
                await self._end_call_session(call_sid, outcome=call_status, duration=call_duration)
            else:
                # No session yet, just log in database if we have candidate info
                logger.warning(f"Call {call_sid} {call_status} - no session found")

    async def _end_call_session(
        self,
        call_sid: str,
        outcome: str,
        duration: Optional[int] = None
    ):
        """End call session and save results"""
        session = self.active_sessions.get(call_sid)
        if not session:
            logger.warning(f"No session to end for {call_sid}")
            return

        try:
            # Get conversation summary and analysis
            if outcome == "completed" or outcome == "natural_end" or outcome == "user_ended":
                analysis = await session.ai_engine.analyze_conversation_outcome()
                summary = analysis.get('summary', 'N/A')
                ai_outcome = analysis.get('outcome', 'unknown')
                next_action = analysis.get('next_action', 'N/A')

                # Map AI outcome to candidate status
                status_mapping = {
                    'interested': CandidateStatus.INTERESTED,
                    'not_interested': CandidateStatus.NOT_INTERESTED,
                    'callback_requested': CandidateStatus.CALLBACK_REQUESTED,
                    'appointment_scheduled': CandidateStatus.APPOINTMENT_SCHEDULED,
                    'info_sent': CandidateStatus.INFO_SENT
                }
                new_status = status_mapping.get(ai_outcome, CandidateStatus.CONTACTED)

                # Update candidate status
                self.candidate_manager.update_candidate_status(
                    session.candidate_id,
                    new_status
                )

            else:
                summary = f"Call ended: {outcome}"
                next_action = "Retry call later" if outcome in ['no-answer', 'busy'] else "Review needed"

            # Get full transcript
            conversation = session.ai_engine.get_conversation_summary()
            transcript = "\n\n".join([
                f"{msg['role'].upper()}: {msg['content']}"
                for msg in conversation['messages']
            ])

            # Update call log
            actual_duration = duration if duration else session.get_duration_seconds()
            self.candidate_manager.update_call_log(
                call_log_id=session.call_log_id,
                ended_at=datetime.now().isoformat(),
                duration_seconds=actual_duration,
                outcome=outcome,
                transcript=transcript,
                summary=summary,
                next_action=next_action
            )

            logger.info(f"Call session {call_sid} ended: {outcome}, duration: {actual_duration}s")

        except Exception as e:
            logger.error(f"Error ending call session: {e}")

        finally:
            # Remove from active sessions
            if call_sid in self.active_sessions:
                del self.active_sessions[call_sid]

    @staticmethod
    def _is_goodbye(text: str) -> bool:
        """Detect if user wants to end call"""
        goodbye_phrases = [
            'tschüss', 'auf wiedersehen', 'wiederhören', 'bye', 'ciao',
            'kein interesse', 'nicht interessiert', 'beenden', 'auflegen'
        ]
        text_lower = text.lower()
        return any(phrase in text_lower for phrase in goodbye_phrases)

    @staticmethod
    def _is_ai_goodbye(text: str) -> bool:
        """Detect if AI is ending conversation"""
        goodbye_phrases = [
            'auf wiederhören', 'vielen dank für ihre zeit',
            'bis bald', 'wir melden uns', 'tschüss'
        ]
        text_lower = text.lower()
        return any(phrase in text_lower for phrase in goodbye_phrases)


# Global handler instance
call_handler = CallHandler()
