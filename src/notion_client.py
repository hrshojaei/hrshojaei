"""
Notion API integration for candidate and call log management
"""
from typing import Optional, Dict, List, Any
from datetime import datetime
from loguru import logger
from notion_client import Client as NotionClient, APIResponseError

from src.config import settings


class RecruitingNotionClient:
    """Manages Notion database integration for recruiting data"""

    def __init__(self, api_key: Optional[str] = None, database_id: Optional[str] = None):
        """Initialize Notion client"""
        self.api_key = api_key or settings.notion_api_key
        self.database_id = database_id or settings.notion_database_id
        self.enabled = settings.notion_enabled and self.api_key and self.database_id

        if self.enabled:
            self.client = NotionClient(auth=self.api_key)
            logger.info("Notion client initialized")
        else:
            self.client = None
            logger.info("Notion integration disabled")

    def is_enabled(self) -> bool:
        """Check if Notion integration is enabled"""
        return self.enabled

    async def create_or_update_candidate(
        self,
        candidate_id: int,
        name: str,
        phone: str,
        email: Optional[str] = None,
        current_company: Optional[str] = None,
        current_position: Optional[str] = None,
        experience_years: Optional[int] = None,
        status: str = "new",
        notes: Optional[str] = None,
        last_call_date: Optional[datetime] = None,
        last_call_outcome: Optional[str] = None
    ) -> Optional[str]:
        """
        Create or update a candidate in Notion database
        Returns: Notion page ID if successful, None otherwise
        """
        if not self.enabled:
            logger.debug("Notion is disabled, skipping candidate sync")
            return None

        try:
            # Check if candidate already exists
            existing_page = await self._find_candidate_by_id(candidate_id)

            properties = self._build_candidate_properties(
                candidate_id=candidate_id,
                name=name,
                phone=phone,
                email=email,
                current_company=current_company,
                current_position=current_position,
                experience_years=experience_years,
                status=status,
                notes=notes,
                last_call_date=last_call_date,
                last_call_outcome=last_call_outcome
            )

            if existing_page:
                # Update existing page
                page_id = existing_page['id']
                self.client.pages.update(
                    page_id=page_id,
                    properties=properties
                )
                logger.info(f"Updated candidate {candidate_id} in Notion: {page_id}")
                return page_id
            else:
                # Create new page
                response = self.client.pages.create(
                    parent={"database_id": self.database_id},
                    properties=properties
                )
                page_id = response['id']
                logger.info(f"Created candidate {candidate_id} in Notion: {page_id}")
                return page_id

        except APIResponseError as e:
            logger.error(f"Notion API error for candidate {candidate_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error syncing candidate {candidate_id} to Notion: {e}")
            return None

    async def add_call_log(
        self,
        candidate_id: int,
        candidate_name: str,
        call_sid: str,
        duration: int,
        outcome: str,
        summary: Optional[str] = None,
        next_action: Optional[str] = None,
        call_timestamp: Optional[datetime] = None
    ) -> Optional[str]:
        """
        Add a call log entry as a comment or separate database entry
        Returns: Notion page/comment ID if successful
        """
        if not self.enabled:
            return None

        try:
            # Find candidate page
            candidate_page = await self._find_candidate_by_id(candidate_id)

            if not candidate_page:
                logger.warning(f"Candidate {candidate_id} not found in Notion, creating...")
                candidate_page_id = await self.create_or_update_candidate(
                    candidate_id=candidate_id,
                    name=candidate_name,
                    phone="",
                    status="contacted"
                )
            else:
                candidate_page_id = candidate_page['id']

            # Create call log as a comment on the candidate page
            call_time = call_timestamp or datetime.now()
            duration_min = duration // 60
            duration_sec = duration % 60

            comment_text = f"""📞 Anruf-Log (Call SID: {call_sid})
**Datum:** {call_time.strftime('%d.%m.%Y %H:%M')}
**Dauer:** {duration_min}m {duration_sec}s
**Ergebnis:** {outcome}

{f'**Zusammenfassung:** {summary}' if summary else ''}
{f'**Nächster Schritt:** {next_action}' if next_action else ''}
"""

            # Add comment to page
            self.client.comments.create(
                parent={"page_id": candidate_page_id},
                rich_text=[{
                    "type": "text",
                    "text": {"content": comment_text}
                }]
            )

            # Also update candidate status
            await self._update_candidate_call_status(
                candidate_page_id,
                call_date=call_time,
                outcome=outcome
            )

            logger.info(f"Added call log to Notion for candidate {candidate_id}")
            return candidate_page_id

        except Exception as e:
            logger.error(f"Error adding call log to Notion: {e}")
            return None

    async def _find_candidate_by_id(self, candidate_id: int) -> Optional[Dict]:
        """Find candidate page by candidate_id"""
        try:
            response = self.client.databases.query(
                database_id=self.database_id,
                filter={
                    "property": "Candidate ID",
                    "number": {
                        "equals": candidate_id
                    }
                }
            )

            if response['results']:
                return response['results'][0]
            return None

        except Exception as e:
            logger.error(f"Error finding candidate {candidate_id}: {e}")
            return None

    async def _update_candidate_call_status(
        self,
        page_id: str,
        call_date: datetime,
        outcome: str
    ):
        """Update candidate's last call date and outcome"""
        try:
            self.client.pages.update(
                page_id=page_id,
                properties={
                    "Letzter Anruf": {
                        "date": {"start": call_date.isoformat()}
                    },
                    "Anruf-Ergebnis": {
                        "select": {"name": outcome}
                    },
                    "Status": {
                        "select": {"name": "contacted"}
                    }
                }
            )
        except Exception as e:
            logger.warning(f"Could not update call status: {e}")

    def _build_candidate_properties(
        self,
        candidate_id: int,
        name: str,
        phone: str,
        email: Optional[str],
        current_company: Optional[str],
        current_position: Optional[str],
        experience_years: Optional[int],
        status: str,
        notes: Optional[str],
        last_call_date: Optional[datetime],
        last_call_outcome: Optional[str]
    ) -> Dict[str, Any]:
        """Build Notion properties dictionary"""
        properties = {
            "Name": {
                "title": [{"text": {"content": name}}]
            },
            "Candidate ID": {
                "number": candidate_id
            },
            "Telefon": {
                "phone_number": phone
            },
            "Status": {
                "select": {"name": status}
            }
        }

        if email:
            properties["Email"] = {"email": email}

        if current_company:
            properties["Aktueller Arbeitgeber"] = {
                "rich_text": [{"text": {"content": current_company}}]
            }

        if current_position:
            properties["Position"] = {
                "rich_text": [{"text": {"content": current_position}}]
            }

        if experience_years is not None:
            properties["Berufserfahrung (Jahre)"] = {
                "number": experience_years
            }

        if notes:
            properties["Notizen"] = {
                "rich_text": [{"text": {"content": notes}}]
            }

        if last_call_date:
            properties["Letzter Anruf"] = {
                "date": {"start": last_call_date.isoformat()}
            }

        if last_call_outcome:
            properties["Anruf-Ergebnis"] = {
                "select": {"name": last_call_outcome}
            }

        return properties

    async def create_database_template(self) -> Optional[str]:
        """
        Create a template database structure in Notion
        Note: This requires a parent page ID where the database will be created
        """
        if not self.enabled:
            logger.error("Notion is not enabled")
            return None

        logger.info("To create a Notion database, please:")
        logger.info("1. Go to Notion and create a new database")
        logger.info("2. Add the following properties:")
        logger.info("   - Name (Title)")
        logger.info("   - Candidate ID (Number)")
        logger.info("   - Telefon (Phone)")
        logger.info("   - Email (Email)")
        logger.info("   - Status (Select: new, contacted, interested, not_interested, callback)")
        logger.info("   - Aktueller Arbeitgeber (Text)")
        logger.info("   - Position (Text)")
        logger.info("   - Berufserfahrung (Jahre) (Number)")
        logger.info("   - Notizen (Text)")
        logger.info("   - Letzter Anruf (Date)")
        logger.info("   - Anruf-Ergebnis (Select: interested, not_interested, callback_requested, etc.)")
        logger.info("3. Share the database with your integration")
        logger.info("4. Copy the database ID from the URL")

        return None


# Global Notion client instance
notion_client = RecruitingNotionClient()
