"""
Candidate management system with SQLite database
"""
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict
from dataclasses import dataclass, asdict
from enum import Enum
import json
import asyncio
from loguru import logger


class CandidateStatus(str, Enum):
    """Candidate status enum"""
    NEW = "new"
    CONTACTED = "contacted"
    INTERESTED = "interested"
    NOT_INTERESTED = "not_interested"
    CALLBACK_REQUESTED = "callback_requested"
    APPOINTMENT_SCHEDULED = "appointment_scheduled"
    INFO_SENT = "info_sent"
    HIRED = "hired"


@dataclass
class Candidate:
    """Candidate data model"""
    id: Optional[int] = None
    name: str = ""
    phone: str = ""
    email: Optional[str] = None
    current_company: Optional[str] = None
    current_position: Optional[str] = None
    experience_years: Optional[int] = None
    status: str = CandidateStatus.NEW
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    last_contact_at: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class CallLog:
    """Call log data model"""
    id: Optional[int] = None
    candidate_id: int = 0
    call_sid: Optional[str] = None
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    duration_seconds: Optional[int] = None
    outcome: Optional[str] = None
    transcript: Optional[str] = None
    summary: Optional[str] = None
    next_action: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {k: v for k, v in asdict(self).items() if v is not None}


class CandidateManager:
    """Manages candidates and call logs in SQLite database"""

    def __init__(self, db_path: str = "./data/candidates.db"):
        self.db_path = db_path
        self._init_database()
        
        # Initialize integrations
        from src.notion_client import notion_client
        from src.n8n_webhook import n8n_webhook
        self.notion_client = notion_client
        self.n8n_webhook = n8n_webhook

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_database(self):
        """Initialize database schema"""
        with self._get_connection() as conn:
            # Candidates table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS candidates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT UNIQUE NOT NULL,
                    email TEXT,
                    current_company TEXT,
                    current_position TEXT,
                    experience_years INTEGER,
                    status TEXT DEFAULT 'new',
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_contact_at TIMESTAMP
                )
            """)

            # Call logs table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS call_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    candidate_id INTEGER NOT NULL,
                    call_sid TEXT,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ended_at TIMESTAMP,
                    duration_seconds INTEGER,
                    outcome TEXT,
                    transcript TEXT,
                    summary TEXT,
                    next_action TEXT,
                    FOREIGN KEY (candidate_id) REFERENCES candidates (id)
                )
            """)

            # Conversation history table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    call_log_id INTEGER NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    role TEXT NOT NULL,
                    message TEXT NOT NULL,
                    FOREIGN KEY (call_log_id) REFERENCES call_logs (id)
                )
            """)

            conn.commit()
            logger.info(f"Database initialized at {self.db_path}")

    def add_candidate(
        self,
        name: str,
        phone: str,
        email: Optional[str] = None,
        current_company: Optional[str] = None,
        current_position: Optional[str] = None,
        experience_years: Optional[int] = None,
        notes: Optional[str] = None
    ) -> int:
        """Add a new candidate"""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO candidates
                (name, phone, email, current_company, current_position, experience_years, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, phone, email, current_company, current_position, experience_years, notes))
            conn.commit()
            candidate_id = cursor.lastrowid
            logger.info(f"Added candidate: {name} (ID: {candidate_id})")
            
            # Sync to Notion and send n8n event
            asyncio.create_task(self._sync_new_candidate(
                candidate_id, name, phone, email, current_company, 
                current_position, experience_years, notes
            ))
            
            return candidate_id
    
    async def _sync_new_candidate(
        self, candidate_id, name, phone, email, 
        current_company, current_position, experience_years, notes
    ):
        """Sync new candidate to Notion and n8n"""
        # Sync to Notion
        await self.notion_client.create_or_update_candidate(
            candidate_id=candidate_id,
            name=name,
            phone=phone,
            email=email,
            current_company=current_company,
            current_position=current_position,
            experience_years=experience_years,
            status="new",
            notes=notes
        )
        
        # Send n8n event
        await self.n8n_webhook.candidate_created(
            candidate_id=candidate_id,
            name=name,
            phone=phone,
            email=email,
            company=current_company
        )

    def get_candidate(self, candidate_id: Optional[int] = None, phone: Optional[str] = None) -> Optional[Candidate]:
        """Get candidate by ID or phone"""
        with self._get_connection() as conn:
            if candidate_id:
                row = conn.execute("SELECT * FROM candidates WHERE id = ?", (candidate_id,)).fetchone()
            elif phone:
                row = conn.execute("SELECT * FROM candidates WHERE phone = ?", (phone,)).fetchone()
            else:
                return None

            if row:
                return Candidate(**dict(row))
            return None

    def update_candidate_status(self, candidate_id: int, status: CandidateStatus):
        """Update candidate status"""
        # Get candidate before update for comparison
        candidate = self.get_candidate(candidate_id)
        old_status = candidate.status if candidate else None
        
        with self._get_connection() as conn:
            conn.execute("""
                UPDATE candidates
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status.value, candidate_id))
            conn.commit()
            logger.info(f"Updated candidate {candidate_id} status to {status.value}")
        
        # Sync to Notion and n8n
        if candidate:
            asyncio.create_task(self._sync_candidate_status_update(
                candidate_id, candidate.name, status.value, old_status
            ))
    
    async def _sync_candidate_status_update(
        self, candidate_id, name, new_status, old_status
    ):
        """Sync candidate status update to Notion and n8n"""
        # Get full candidate data
        candidate = self.get_candidate(candidate_id)
        if not candidate:
            return
        
        # Sync to Notion
        await self.notion_client.create_or_update_candidate(
            candidate_id=candidate_id,
            name=candidate.name,
            phone=candidate.phone,
            email=candidate.email,
            current_company=candidate.current_company,
            current_position=candidate.current_position,
            experience_years=candidate.experience_years,
            status=new_status,
            notes=candidate.notes
        )
        
        # Send n8n event
        await self.n8n_webhook.candidate_updated(
            candidate_id=candidate_id,
            name=name,
            status=new_status,
            changes={"status": {"from": old_status, "to": new_status}}
        )
        
        # Special event if candidate is interested
        if new_status == CandidateStatus.INTERESTED.value:
            await self.n8n_webhook.candidate_interested(
                candidate_id=candidate_id,
                candidate_name=name,
                phone=candidate.phone,
                email=candidate.email,
                notes=candidate.notes
            )

    def update_last_contact(self, candidate_id: int):
        """Update last contact timestamp"""
        with self._get_connection() as conn:
            conn.execute("""
                UPDATE candidates
                SET last_contact_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (candidate_id,))
            conn.commit()

    def get_candidates_to_call(self, limit: int = 10) -> List[Candidate]:
        """Get candidates that need to be called"""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM candidates
                WHERE status IN ('new', 'callback_requested')
                ORDER BY
                    CASE status
                        WHEN 'callback_requested' THEN 1
                        WHEN 'new' THEN 2
                    END,
                    created_at ASC
                LIMIT ?
            """, (limit,)).fetchall()

            return [Candidate(**dict(row)) for row in rows]

    def create_call_log(self, candidate_id: int, call_sid: Optional[str] = None) -> int:
        """Create a new call log"""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO call_logs (candidate_id, call_sid)
                VALUES (?, ?)
            """, (candidate_id, call_sid))
            conn.commit()
            call_log_id = cursor.lastrowid
            logger.info(f"Created call log {call_log_id} for candidate {candidate_id}")
            return call_log_id

    def update_call_log(
        self,
        call_log_id: int,
        ended_at: Optional[str] = None,
        duration_seconds: Optional[int] = None,
        outcome: Optional[str] = None,
        transcript: Optional[str] = None,
        summary: Optional[str] = None,
        next_action: Optional[str] = None
    ):
        """Update call log"""
        with self._get_connection() as conn:
            updates = []
            params = []

            if ended_at:
                updates.append("ended_at = ?")
                params.append(ended_at)
            if duration_seconds is not None:
                updates.append("duration_seconds = ?")
                params.append(duration_seconds)
            if outcome:
                updates.append("outcome = ?")
                params.append(outcome)
            if transcript:
                updates.append("transcript = ?")
                params.append(transcript)
            if summary:
                updates.append("summary = ?")
                params.append(summary)
            if next_action:
                updates.append("next_action = ?")
                params.append(next_action)

            if updates:
                params.append(call_log_id)
                query = f"UPDATE call_logs SET {', '.join(updates)} WHERE id = ?"
                conn.execute(query, params)
                conn.commit()
                logger.info(f"Updated call log {call_log_id}")
                
                # If call ended, sync to Notion and n8n
                if ended_at or outcome:
                    asyncio.create_task(self._sync_call_completion(
                        call_log_id, duration_seconds, outcome, summary, next_action
                    ))
    
    async def _sync_call_completion(
        self, call_log_id, duration_seconds, outcome, summary, next_action
    ):
        """Sync call completion to Notion and n8n"""
        # Get call log and candidate info
        call_log = self.get_call_log(call_log_id)
        if not call_log:
            return
        
        candidate = self.get_candidate(call_log.candidate_id)
        if not candidate:
            return
        
        # Sync to Notion
        await self.notion_client.add_call_log(
            candidate_id=candidate.id,
            candidate_name=candidate.name,
            call_sid=call_log.call_sid or f"call_{call_log_id}",
            duration=duration_seconds or 0,
            outcome=outcome or "unknown",
            summary=summary,
            next_action=next_action,
            call_timestamp=datetime.fromisoformat(call_log.started_at) if call_log.started_at else datetime.now()
        )
        
        # Send n8n event
        await self.n8n_webhook.call_completed(
            call_sid=call_log.call_sid or f"call_{call_log_id}",
            candidate_id=candidate.id,
            candidate_name=candidate.name,
            duration=duration_seconds or 0,
            outcome=outcome or "unknown",
            summary=summary,
            next_action=next_action
        )
        
        # Handle special cases
        if outcome == CandidateStatus.CALLBACK_REQUESTED.value:
            await self.n8n_webhook.callback_requested(
                candidate_id=candidate.id,
                candidate_name=candidate.name,
                phone=candidate.phone,
                requested_time=next_action
            )

    def add_conversation_message(self, call_log_id: int, role: str, message: str):
        """Add a message to conversation history"""
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO conversation_history (call_log_id, role, message)
                VALUES (?, ?, ?)
            """, (call_log_id, role, message))
            conn.commit()
    
    def get_call_log(self, call_log_id: int) -> Optional[CallLog]:
        """Get call log by ID"""
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM call_logs WHERE id = ?", (call_log_id,)).fetchone()
            if row:
                return CallLog(**dict(row))
            return None

    def get_conversation_history(self, call_log_id: int) -> List[Dict]:
        """Get conversation history for a call"""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT role, message, timestamp
                FROM conversation_history
                WHERE call_log_id = ?
                ORDER BY timestamp ASC
            """, (call_log_id,)).fetchall()

            return [dict(row) for row in rows]

    def get_candidate_history(self, candidate_id: int) -> List[CallLog]:
        """Get all call logs for a candidate"""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM call_logs
                WHERE candidate_id = ?
                ORDER BY started_at DESC
            """, (candidate_id,)).fetchall()

            return [CallLog(**dict(row)) for row in rows]

    def get_statistics(self) -> Dict:
        """Get overall statistics"""
        with self._get_connection() as conn:
            stats = {}

            # Total candidates
            stats['total_candidates'] = conn.execute(
                "SELECT COUNT(*) as count FROM candidates"
            ).fetchone()['count']

            # Candidates by status
            status_rows = conn.execute("""
                SELECT status, COUNT(*) as count
                FROM candidates
                GROUP BY status
            """).fetchall()
            stats['by_status'] = {row['status']: row['count'] for row in status_rows}

            # Total calls
            stats['total_calls'] = conn.execute(
                "SELECT COUNT(*) as count FROM call_logs"
            ).fetchone()['count']

            # Average call duration
            avg_duration = conn.execute("""
                SELECT AVG(duration_seconds) as avg
                FROM call_logs
                WHERE duration_seconds IS NOT NULL
            """).fetchone()['avg']
            stats['avg_call_duration_seconds'] = round(avg_duration) if avg_duration else 0

            return stats


# CLI interface for testing
if __name__ == "__main__":
    import sys

    manager = CandidateManager()

    if len(sys.argv) > 1 and sys.argv[1] == "init":
        print("✓ Database initialized")

    elif len(sys.argv) > 1 and sys.argv[1] == "stats":
        stats = manager.get_statistics()
        print("\n📊 Statistics:")
        print(f"Total Candidates: {stats['total_candidates']}")
        print(f"Total Calls: {stats['total_calls']}")
        print(f"Avg Call Duration: {stats['avg_call_duration_seconds']}s")
        print("\nBy Status:")
        for status, count in stats['by_status'].items():
            print(f"  {status}: {count}")

    elif len(sys.argv) > 1 and sys.argv[1] == "add":
        # Example: python -m src.candidate_manager add "Max Mustermann" "+4915112345678"
        if len(sys.argv) >= 4:
            name = sys.argv[2]
            phone = sys.argv[3]
            candidate_id = manager.add_candidate(name=name, phone=phone)
            print(f"✓ Added candidate: {name} (ID: {candidate_id})")
        else:
            print("Usage: python -m src.candidate_manager add <name> <phone>")

    else:
        print("Usage:")
        print("  python -m src.candidate_manager init     - Initialize database")
        print("  python -m src.candidate_manager stats    - Show statistics")
        print("  python -m src.candidate_manager add <name> <phone>  - Add candidate")
