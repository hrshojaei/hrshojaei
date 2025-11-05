"""
Sipgate REST API Client
Handles outbound calls and webhooks for Sipgate telephony
"""
import base64
import httpx
from typing import Optional, Dict, Any
from loguru import logger


class SipgateClient:
    """Client for Sipgate REST API v2"""

    def __init__(
        self,
        phone_number: str,
        webhook_url: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
        token_id: Optional[str] = None,
        token: Optional[str] = None,
        device_id: Optional[str] = None
    ):
        """
        Initialize Sipgate client

        Args:
            phone_number: Your Sipgate phone number (E.164 format, e.g. +4922838755035)
            webhook_url: Base URL for webhooks (e.g. https://candidateai.de)
            email: Sipgate account email (for Basic Auth)
            password: Sipgate account password (for Basic Auth)
            token_id: Sipgate API token ID (for Token Auth - recommended)
            token: Sipgate API token secret (for Token Auth - recommended)
            device_id: Device ID for making calls (e.g. 'y0'). If not provided, will be auto-detected.
        """
        self.phone_number = phone_number
        self.webhook_url = webhook_url
        self.base_url = "https://api.sipgate.com/v2"
        self.device_id = device_id  # Store device ID

        # Create Basic Auth header - prefer token over email/password
        if token_id and token:
            credentials = f"{token_id}:{token}"
            logger.info(f"Sipgate client using Token authentication")
        elif email and password:
            credentials = f"{email}:{password}"
            logger.info(f"Sipgate client using Email/Password authentication")
        else:
            raise ValueError("Either (token_id + token) or (email + password) must be provided")

        encoded = base64.b64encode(credentials.encode()).decode()
        self.headers = {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/json"
        }

        logger.info(f"Sipgate client initialized for {phone_number} (device: {device_id or 'auto-detect'})")

    async def make_call(
        self,
        to_number: str,
        caller_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Initiate an outbound call

        Args:
            to_number: Destination phone number (E.164 format)
            caller_id: Optional caller ID to display

        Returns:
            Dict with call information including session_id
        """
        if not caller_id:
            caller_id = self.phone_number

        # Normalize phone numbers to E.164
        to_number = self._normalize_number(to_number)
        caller_id = self._normalize_number(caller_id)

        # Get device ID (use stored one or auto-detect)
        device_id = await self._get_device_id()

        payload = {
            "deviceId": device_id,
            "caller": caller_id,
            "callee": to_number,
            "callerId": caller_id
        }

        # Add webhook URL if provided
        if self.webhook_url:
            payload["webhookUrl"] = f"{self.webhook_url}/webhook/sipgate/call"

        logger.info(f"Making call from {caller_id} to {to_number}")

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/sessions/calls",
                    json=payload,
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()

                result = response.json()
                session_id = result.get("sessionId")

                logger.info(f"Call initiated successfully: {session_id}")

                return {
                    "success": True,
                    "session_id": session_id,
                    "to": to_number,
                    "from": caller_id
                }

            except httpx.HTTPStatusError as e:
                error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
                logger.error(f"Failed to make call: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg
                }
            except Exception as e:
                logger.error(f"Error making call: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }

    def _normalize_number(self, number: str) -> str:
        """
        Normalize phone number to E.164 format

        Args:
            number: Phone number in various formats

        Returns:
            E.164 formatted number (e.g. +4922838755035)
        """
        # Remove all non-digit characters except +
        cleaned = ''.join(c for c in number if c.isdigit() or c == '+')

        # If starts with 0, assume German number
        if cleaned.startswith('0'):
            cleaned = '+49' + cleaned[1:]

        # If doesn't start with +, add it
        if not cleaned.startswith('+'):
            cleaned = '+' + cleaned

        return cleaned

    async def _get_device_id(self) -> str:
        """
        Get device ID for making calls.
        Uses stored device_id if available, otherwise auto-detects from account.

        Returns:
            Device ID (e.g. 'y0')
        """
        # If device_id was provided in constructor, use it
        if self.device_id:
            return self.device_id

        # Auto-detect device ID from account
        logger.info("Auto-detecting device ID from Sipgate account...")

        async with httpx.AsyncClient() as client:
            try:
                # Get user info to find the sub (user ID like 'w0')
                user_response = await client.get(
                    f"{self.base_url}/authorization/userinfo",
                    headers=self.headers,
                    timeout=10.0
                )
                user_response.raise_for_status()
                user_id = user_response.json().get("sub", "w0")

                # Get devices for this user
                devices_response = await client.get(
                    f"{self.base_url}/{user_id}/devices",
                    headers=self.headers,
                    timeout=10.0
                )
                devices_response.raise_for_status()
                devices = devices_response.json().get("items", [])

                if not devices:
                    logger.error("No devices found in account")
                    raise ValueError("No devices found. Please configure SIPGATE_DEVICE_ID manually.")

                # Use first available device
                first_device = devices[0]
                device_id = first_device.get("id")

                logger.info(f"Auto-detected device ID: {device_id} ({first_device.get('alias')})")

                # Cache it for future calls
                self.device_id = device_id

                return device_id

            except Exception as e:
                logger.error(f"Failed to auto-detect device ID: {e}")
                raise ValueError(f"Could not detect device ID. Please set SIPGATE_DEVICE_ID in .env. Error: {e}")

    async def get_account_info(self) -> Dict[str, Any]:
        """
        Get account information including balance and device IDs

        Returns:
            Account information dict
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/account",
                    headers=self.headers,
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()

            except Exception as e:
                logger.error(f"Error getting account info: {e}")
                return {"error": str(e)}

    async def get_balance(self) -> Optional[float]:
        """
        Get current account balance

        Returns:
            Balance in EUR or None if error
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/balance",
                    headers=self.headers,
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
                balance = data.get("amount")

                logger.info(f"Current balance: €{balance}")
                return balance

            except Exception as e:
                logger.error(f"Error getting balance: {e}")
                return None


class SipgateXMLResponse:
    """Helper class to generate Sipgate XML responses for webhooks"""

    @staticmethod
    def dial(number: str) -> str:
        """
        Generate XML to dial a number

        Args:
            number: Phone number to dial

        Returns:
            Sipgate XML string
        """
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Dial>{number}</Dial>
</Response>"""

    @staticmethod
    def play(url: str) -> str:
        """
        Generate XML to play an audio file

        Args:
            url: URL of audio file to play

        Returns:
            Sipgate XML string
        """
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Play>{url}</Play>
</Response>"""

    @staticmethod
    def gather(action_url: str, timeout: int = 5) -> str:
        """
        Generate XML to gather DTMF input

        Args:
            action_url: URL to POST gathered digits
            timeout: Timeout in seconds

        Returns:
            Sipgate XML string
        """
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather action="{action_url}" timeout="{timeout}" />
</Response>"""

    @staticmethod
    def hangup() -> str:
        """
        Generate XML to hang up the call

        Returns:
            Sipgate XML string
        """
        return """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Hangup/>
</Response>"""

    @staticmethod
    def redirect(url: str) -> str:
        """
        Generate XML to redirect to another webhook

        Args:
            url: Webhook URL to redirect to

        Returns:
            Sipgate XML string
        """
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Redirect>{url}</Redirect>
</Response>"""
