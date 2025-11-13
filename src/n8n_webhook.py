"""
n8n Webhook integration for workflow automation
"""
from typing import Optional, Dict, Any
from datetime import datetime
import httpx
from loguru import logger

from src.config import settings


class N8NWebhookClient:
    """Sends events to n8n for workflow automation"""

    def __init__(self, webhook_url: Optional[str] = None):
        """Initialize n8n webhook client"""
        self.webhook_url = webhook_url or settings.n8n_webhook_url
        self.enabled = settings.n8n_enabled and self.webhook_url

        if self.enabled:
            logger.info(f"n8n webhook client initialized: {self.webhook_url}")
        else:
            logger.info("n8n webhook integration disabled")

    def is_enabled(self) -> bool:
        """Check if n8n integration is enabled"""
        return self.enabled

    async def send_event(self, event_type: str, data: Dict[str, Any]) -> bool:
        """
        Send an event to n8n webhook
        
        Args:
            event_type: Type of event (e.g., 'candidate.created', 'call.completed')
            data: Event data
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            logger.debug(f"n8n disabled, skipping event: {event_type}")
            return False

        try:
            payload = {
                "event": event_type,
                "timestamp": datetime.now().isoformat(),
                "data": data
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.webhook_url,
                    json=payload,
                    timeout=10.0
                )

                if response.status_code in [200, 201, 204]:
                    logger.info(f"n8n event sent successfully: {event_type}")
                    return True
                else:
                    logger.warning(f"n8n webhook returned status {response.status_code}: {event_type}")
                    return False

        except httpx.TimeoutException:
            logger.error(f"n8n webhook timeout for event: {event_type}")
            return False
        except Exception as e:
            logger.error(f"Error sending n8n event {event_type}: {e}")
            return False

    async def candidate_created(
        self,
        candidate_id: int,
        name: str,
        phone: str,
        email: Optional[str] = None,
        company: Optional[str] = None
    ) -> bool:
        """Send candidate.created event"""
        return await self.send_event("candidate.created", {
            "candidate_id": candidate_id,
            "name": name,
            "phone": phone,
            "email": email,
            "company": company
        })

    async def candidate_updated(
        self,
        candidate_id: int,
        name: str,
        status: str,
        changes: Dict[str, Any]
    ) -> bool:
        """Send candidate.updated event"""
        return await self.send_event("candidate.updated", {
            "candidate_id": candidate_id,
            "name": name,
            "status": status,
            "changes": changes
        })

    async def call_started(
        self,
        call_sid: str,
        candidate_id: int,
        candidate_name: str,
        phone: str
    ) -> bool:
        """Send call.started event"""
        return await self.send_event("call.started", {
            "call_sid": call_sid,
            "candidate_id": candidate_id,
            "candidate_name": candidate_name,
            "phone": phone
        })

    async def call_completed(
        self,
        call_sid: str,
        candidate_id: int,
        candidate_name: str,
        duration: int,
        outcome: str,
        summary: Optional[str] = None,
        next_action: Optional[str] = None
    ) -> bool:
        """Send call.completed event"""
        return await self.send_event("call.completed", {
            "call_sid": call_sid,
            "candidate_id": candidate_id,
            "candidate_name": candidate_name,
            "duration_seconds": duration,
            "outcome": outcome,
            "summary": summary,
            "next_action": next_action
        })

    async def candidate_interested(
        self,
        candidate_id: int,
        candidate_name: str,
        phone: str,
        email: Optional[str] = None,
        notes: Optional[str] = None
    ) -> bool:
        """Send candidate.interested event (high priority)"""
        return await self.send_event("candidate.interested", {
            "candidate_id": candidate_id,
            "candidate_name": candidate_name,
            "phone": phone,
            "email": email,
            "notes": notes,
            "priority": "high"
        })

    async def callback_requested(
        self,
        candidate_id: int,
        candidate_name: str,
        phone: str,
        requested_time: Optional[str] = None
    ) -> bool:
        """Send callback.requested event"""
        return await self.send_event("callback.requested", {
            "candidate_id": candidate_id,
            "candidate_name": candidate_name,
            "phone": phone,
            "requested_time": requested_time
        })


# Global n8n webhook client instance
n8n_webhook = N8NWebhookClient()
