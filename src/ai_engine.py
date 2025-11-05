"""
AI Conversation Engine using Claude or OpenAI
"""
from typing import List, Dict, Optional, AsyncIterator
from loguru import logger
import anthropic
import openai

from src.config import settings
from src.prompts import get_system_prompt, get_conversation_context


class ConversationMessage:
    """Represents a conversation message"""

    def __init__(self, role: str, content: str):
        self.role = role  # "user", "assistant", or "system"
        self.content = content

    def to_dict(self) -> dict:
        return {"role": self.role, "content": self.content}


class AIConversationEngine:
    """Manages AI-powered conversations"""

    def __init__(self, provider: Optional[str] = None):
        self.provider = provider or settings.ai_provider
        self.conversation_history: List[ConversationMessage] = []

        # Initialize AI client based on provider
        if self.provider == "anthropic":
            if not settings.anthropic_api_key:
                raise ValueError("ANTHROPIC_API_KEY not set")
            self.anthropic_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
            logger.info("Initialized Anthropic Claude client")

        elif self.provider == "openai":
            if not settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY not set")
            self.openai_client = openai.OpenAI(api_key=settings.openai_api_key)
            logger.info("Initialized OpenAI client")

        else:
            raise ValueError(f"Unknown AI provider: {self.provider}")

    def initialize_conversation(self, candidate_data: dict):
        """Initialize a new conversation with system prompt and candidate context"""
        system_prompt = get_system_prompt()
        candidate_context = get_conversation_context(candidate_data)

        full_system_prompt = f"{system_prompt}\n\n{candidate_context}"

        # Store system message (handling differs by provider)
        self.system_prompt = full_system_prompt
        self.conversation_history = []

        logger.info(f"Initialized conversation for candidate: {candidate_data.get('name', 'Unknown')}")

    def add_user_message(self, message: str):
        """Add user message to conversation history"""
        self.conversation_history.append(ConversationMessage("user", message))
        logger.debug(f"User: {message}")

    def add_assistant_message(self, message: str):
        """Add assistant message to conversation history"""
        self.conversation_history.append(ConversationMessage("assistant", message))
        logger.debug(f"Assistant: {message}")

    async def get_response(self, user_input: str) -> str:
        """Get AI response to user input"""
        # Add user message
        self.add_user_message(user_input)

        # Get response from appropriate provider
        if self.provider == "anthropic":
            response = await self._get_claude_response()
        elif self.provider == "openai":
            response = await self._get_openai_response()
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

        # Add assistant response
        self.add_assistant_message(response)

        return response

    async def _get_claude_response(self) -> str:
        """Get response from Claude"""
        try:
            # Convert conversation history to Claude format
            messages = [msg.to_dict() for msg in self.conversation_history]

            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,  # Keep responses concise for phone calls
                system=self.system_prompt,
                messages=messages,
                temperature=0.7
            )

            # Extract text from response
            return response.content[0].text

        except Exception as e:
            logger.error(f"Error getting Claude response: {e}")
            return "Entschuldigung, ich hatte gerade eine kurze Unterbrechung. Könnten Sie das bitte wiederholen?"

    async def _get_openai_response(self) -> str:
        """Get response from OpenAI"""
        try:
            # OpenAI includes system message in messages array
            messages = [{"role": "system", "content": self.system_prompt}]
            messages.extend([msg.to_dict() for msg in self.conversation_history])

            response = self.openai_client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error getting OpenAI response: {e}")
            return "Entschuldigung, ich hatte gerade eine kurze Unterbrechung. Könnten Sie das bitte wiederholen?"

    async def stream_response(self, user_input: str) -> AsyncIterator[str]:
        """Stream AI response (useful for real-time conversations)"""
        self.add_user_message(user_input)

        if self.provider == "anthropic":
            async for chunk in self._stream_claude_response():
                yield chunk

        elif self.provider == "openai":
            async for chunk in self._stream_openai_response():
                yield chunk

    async def _stream_claude_response(self) -> AsyncIterator[str]:
        """Stream response from Claude"""
        try:
            messages = [msg.to_dict() for msg in self.conversation_history]
            full_response = ""

            with self.anthropic_client.messages.stream(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                system=self.system_prompt,
                messages=messages,
                temperature=0.7
            ) as stream:
                for text in stream.text_stream:
                    full_response += text
                    yield text

            # Add complete response to history
            self.add_assistant_message(full_response)

        except Exception as e:
            logger.error(f"Error streaming Claude response: {e}")
            yield "Entschuldigung, ich hatte eine kurze Unterbrechung."

    async def _stream_openai_response(self) -> AsyncIterator[str]:
        """Stream response from OpenAI"""
        try:
            messages = [{"role": "system", "content": self.system_prompt}]
            messages.extend([msg.to_dict() for msg in self.conversation_history])

            full_response = ""

            stream = self.openai_client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                max_tokens=500,
                temperature=0.7,
                stream=True
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    text = chunk.choices[0].delta.content
                    full_response += text
                    yield text

            # Add complete response to history
            self.add_assistant_message(full_response)

        except Exception as e:
            logger.error(f"Error streaming OpenAI response: {e}")
            yield "Entschuldigung, ich hatte eine kurze Unterbrechung."

    def get_conversation_summary(self) -> Dict[str, any]:
        """Generate conversation summary"""
        total_turns = len(self.conversation_history) // 2

        return {
            "total_turns": total_turns,
            "messages": [msg.to_dict() for msg in self.conversation_history],
            "provider": self.provider
        }

    async def analyze_conversation_outcome(self) -> Dict[str, str]:
        """Analyze the conversation to determine outcome and next steps"""
        # Create analysis prompt
        conversation_text = "\n".join([
            f"{msg.role.upper()}: {msg.content}"
            for msg in self.conversation_history
        ])

        analysis_prompt = f"""Analysiere folgendes Recruiting-Gespräch und beantworte:

1. OUTCOME: Was war das Ergebnis? (interested/not_interested/callback_requested/appointment_scheduled/info_sent)
2. SUMMARY: Fasse das Gespräch in 2-3 Sätzen zusammen
3. NEXT_ACTION: Was ist der nächste Schritt?

GESPRÄCH:
{conversation_text}

Antworte im JSON-Format:
{{
    "outcome": "...",
    "summary": "...",
    "next_action": "..."
}}"""

        # Get analysis (using same provider)
        if self.provider == "anthropic":
            try:
                response = self.anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=300,
                    messages=[{"role": "user", "content": analysis_prompt}]
                )
                analysis_text = response.content[0].text

            except Exception as e:
                logger.error(f"Error analyzing conversation: {e}")
                analysis_text = '{"outcome": "unknown", "summary": "Fehler bei Analyse", "next_action": "Manual review needed"}'

        else:  # openai
            try:
                response = self.openai_client.chat.completions.create(
                    model=settings.openai_model,
                    messages=[{"role": "user", "content": analysis_prompt}],
                    max_tokens=300
                )
                analysis_text = response.choices[0].message.content

            except Exception as e:
                logger.error(f"Error analyzing conversation: {e}")
                analysis_text = '{"outcome": "unknown", "summary": "Fehler bei Analyse", "next_action": "Manual review needed"}'

        # Parse JSON response
        import json
        try:
            # Extract JSON from response (might be wrapped in markdown)
            if "```json" in analysis_text:
                analysis_text = analysis_text.split("```json")[1].split("```")[0]
            elif "```" in analysis_text:
                analysis_text = analysis_text.split("```")[1].split("```")[0]

            analysis = json.loads(analysis_text.strip())
            return analysis

        except Exception as e:
            logger.error(f"Error parsing analysis: {e}")
            return {
                "outcome": "unknown",
                "summary": "Konnte nicht analysiert werden",
                "next_action": "Manuelle Überprüfung erforderlich"
            }

    def reset(self):
        """Reset conversation history"""
        self.conversation_history = []
        logger.info("Conversation reset")


# Test/CLI interface
if __name__ == "__main__":
    import asyncio

    async def test_conversation():
        """Test conversation flow"""
        engine = AIConversationEngine()

        # Initialize with sample candidate
        candidate_data = {
            "name": "Max Mustermann",
            "current_company": "Hörakustik XY",
            "experience_years": 5
        }

        engine.initialize_conversation(candidate_data)

        print("🤖 AI Conversation Engine Test")
        print("=" * 50)

        # Simulate conversation
        test_inputs = [
            "Hallo?",
            "Ja, ich habe kurz Zeit.",
            "Ich bin seit 5 Jahren Hörakustiker.",
            "Klingt interessant, erzählen Sie mehr."
        ]

        for user_input in test_inputs:
            print(f"\n👤 User: {user_input}")
            response = await engine.get_response(user_input)
            print(f"🤖 Assistant: {response}")

        # Get summary
        print("\n" + "=" * 50)
        print("📊 Conversation Summary:")
        summary = engine.get_conversation_summary()
        print(f"Total turns: {summary['total_turns']}")

        # Analyze outcome
        print("\n📋 Conversation Analysis:")
        analysis = await engine.analyze_conversation_outcome()
        print(f"Outcome: {analysis['outcome']}")
        print(f"Summary: {analysis['summary']}")
        print(f"Next Action: {analysis['next_action']}")

    # Run test
    asyncio.run(test_conversation())
