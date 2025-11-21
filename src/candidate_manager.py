"""
Candidate management system with SQLite database
"""
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict
from dataclasses import dataclass, asdict
from enum import Enum
import json
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

    # DSGVO/Privacy fields
    consent_given: Optional[bool] = None
    consent_timestamp: Optional[str] = None
    consent_method: Optional[str] = None  # 'phone', 'email', 'web', 'sms'
    consent_version: Optional[str] = None  # e.g., "v1.0"
    recording_consent: Optional[bool] = None
    marketing_consent: Optional[bool] = None
    data_retention_until: Optional[str] = None
    opted_out: Optional[bool] = False
    opted_out_at: Optional[str] = None

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

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _migrate_privacy_fields(self, conn: sqlite3.Connection):
        """Add privacy fields to existing candidates table if they don't exist"""
        cursor = conn.cursor()

        # Get existing columns
        cursor.execute("PRAGMA table_info(candidates)")
        existing_columns = {row[1] for row in cursor.fetchall()}

        # Define privacy fields to add
        privacy_fields = {
            'consent_given': 'INTEGER DEFAULT 0',
            'consent_timestamp': 'TIMESTAMP',
            'consent_method': 'TEXT',
            'consent_version': 'TEXT',
            'recording_consent': 'INTEGER DEFAULT 0',
            'marketing_consent': 'INTEGER DEFAULT 0',
            'data_retention_until': 'TIMESTAMP',
            'opted_out': 'INTEGER DEFAULT 0',
            'opted_out_at': 'TIMESTAMP'
        }

        # Add missing columns
        for field_name, field_type in privacy_fields.items():
            if field_name not in existing_columns:
                try:
                    conn.execute(f"ALTER TABLE candidates ADD COLUMN {field_name} {field_type}")
                    logger.info(f"Added privacy field: {field_name}")
                except sqlite3.OperationalError as e:
                    logger.warning(f"Could not add field {field_name}: {e}")

        conn.commit()

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
                    last_contact_at TIMESTAMP,

                    -- DSGVO/Privacy fields
                    consent_given INTEGER DEFAULT 0,
                    consent_timestamp TIMESTAMP,
                    consent_method TEXT,
                    consent_version TEXT,
                    recording_consent INTEGER DEFAULT 0,
                    marketing_consent INTEGER DEFAULT 0,
                    data_retention_until TIMESTAMP,
                    opted_out INTEGER DEFAULT 0,
                    opted_out_at TIMESTAMP
                )
            """)

            # Migrate existing databases: Add privacy columns if they don't exist
            self._migrate_privacy_fields(conn)

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
            return candidate_id

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
        with self._get_connection() as conn:
            conn.execute("""
                UPDATE candidates
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status.value, candidate_id))
            conn.commit()
            logger.info(f"Updated candidate {candidate_id} status to {status.value}")

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

    def add_conversation_message(self, call_log_id: int, role: str, message: str):
        """Add a message to conversation history"""
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO conversation_history (call_log_id, role, message)
                VALUES (?, ?, ?)
            """, (call_log_id, role, message))
            conn.commit()

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

            # Privacy/Consent statistics
            stats['consent_given'] = conn.execute(
                "SELECT COUNT(*) as count FROM candidates WHERE consent_given = 1"
            ).fetchone()['count']
            stats['opted_out'] = conn.execute(
                "SELECT COUNT(*) as count FROM candidates WHERE opted_out = 1"
            ).fetchone()['count']

            return stats

    # ========== DSGVO/Privacy Management Methods ==========

    def set_consent(
        self,
        candidate_id: int,
        consent_given: bool = True,
        consent_method: str = 'phone',
        consent_version: str = 'v1.0',
        recording_consent: bool = False,
        marketing_consent: bool = False,
        retention_days: int = 730  # 2 years default
    ) -> bool:
        """
        Set consent for a candidate

        Args:
            candidate_id: The candidate's ID
            consent_given: Whether consent was given
            consent_method: Method of consent ('phone', 'email', 'web', 'sms')
            consent_version: Version of privacy policy accepted
            recording_consent: Consent for call recording
            marketing_consent: Consent for marketing communications
            retention_days: Number of days to retain data (default: 730 = 2 years)

        Returns:
            bool: Success status
        """
        from datetime import datetime, timedelta

        with self._get_connection() as conn:
            retention_date = (datetime.now() + timedelta(days=retention_days)).isoformat()

            conn.execute("""
                UPDATE candidates
                SET consent_given = ?,
                    consent_timestamp = CURRENT_TIMESTAMP,
                    consent_method = ?,
                    consent_version = ?,
                    recording_consent = ?,
                    marketing_consent = ?,
                    data_retention_until = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                1 if consent_given else 0,
                consent_method,
                consent_version,
                1 if recording_consent else 0,
                1 if marketing_consent else 0,
                retention_date,
                candidate_id
            ))
            conn.commit()

            logger.info(f"Set consent for candidate {candidate_id}: given={consent_given}, method={consent_method}")
            return True

    def revoke_consent(self, candidate_id: int) -> bool:
        """
        Revoke consent and mark candidate as opted out

        Args:
            candidate_id: The candidate's ID

        Returns:
            bool: Success status
        """
        with self._get_connection() as conn:
            conn.execute("""
                UPDATE candidates
                SET opted_out = 1,
                    opted_out_at = CURRENT_TIMESTAMP,
                    consent_given = 0,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (candidate_id,))
            conn.commit()

            logger.info(f"Consent revoked for candidate {candidate_id}")
            return True

    def has_valid_consent(self, candidate_id: int) -> bool:
        """
        Check if candidate has valid consent

        Args:
            candidate_id: The candidate's ID

        Returns:
            bool: True if consent is valid and not opted out
        """
        from datetime import datetime

        candidate = self.get_candidate(candidate_id=candidate_id)
        if not candidate:
            return False

        # Check if opted out
        if candidate.opted_out:
            return False

        # Check if consent given
        if not candidate.consent_given:
            return False

        # Check if data retention period expired
        if candidate.data_retention_until:
            retention_date = datetime.fromisoformat(candidate.data_retention_until)
            if datetime.now() > retention_date:
                logger.warning(f"Data retention expired for candidate {candidate_id}")
                return False

        return True

    def delete_candidate_data(self, candidate_id: int, anonymize: bool = False) -> bool:
        """
        Delete or anonymize candidate data (DSGVO right to erasure)

        Args:
            candidate_id: The candidate's ID
            anonymize: If True, anonymize instead of delete

        Returns:
            bool: Success status
        """
        with self._get_connection() as conn:
            if anonymize:
                # Anonymize personal data but keep record for statistics
                conn.execute("""
                    UPDATE candidates
                    SET name = 'ANONYMIZED',
                        phone = 'DELETED_' || id,
                        email = NULL,
                        current_company = NULL,
                        current_position = NULL,
                        notes = 'Data anonymized per DSGVO request',
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (candidate_id,))

                # Anonymize call transcripts
                conn.execute("""
                    UPDATE call_logs
                    SET transcript = 'ANONYMIZED',
                        summary = 'Data anonymized per DSGVO request'
                    WHERE candidate_id = ?
                """, (candidate_id,))

                logger.info(f"Anonymized data for candidate {candidate_id}")
            else:
                # Full deletion
                conn.execute("DELETE FROM conversation_history WHERE call_log_id IN (SELECT id FROM call_logs WHERE candidate_id = ?)", (candidate_id,))
                conn.execute("DELETE FROM call_logs WHERE candidate_id = ?", (candidate_id,))
                conn.execute("DELETE FROM candidates WHERE id = ?", (candidate_id,))
                logger.info(f"Deleted all data for candidate {candidate_id}")

            conn.commit()
            return True

    def export_candidate_data(self, candidate_id: int) -> Optional[Dict]:
        """
        Export all candidate data (DSGVO right to data portability)

        Args:
            candidate_id: The candidate's ID

        Returns:
            Dict: All candidate data including call history
        """
        candidate = self.get_candidate(candidate_id=candidate_id)
        if not candidate:
            return None

        call_history = self.get_candidate_history(candidate_id)

        # Build complete export
        export_data = {
            'candidate': candidate.to_dict(),
            'call_logs': [call.to_dict() for call in call_history],
            'conversation_history': []
        }

        # Add conversation history for each call
        for call in call_history:
            if call.id:
                conversations = self.get_conversation_history(call.id)
                export_data['conversation_history'].extend(conversations)

        logger.info(f"Exported data for candidate {candidate_id}")
        return export_data

    def get_candidates_needing_deletion(self) -> List[Candidate]:
        """
        Get candidates whose data retention period has expired

        Returns:
            List[Candidate]: Candidates that should be deleted
        """
        from datetime import datetime

        with self._get_connection() as conn:
            now = datetime.now().isoformat()
            rows = conn.execute("""
                SELECT * FROM candidates
                WHERE data_retention_until IS NOT NULL
                AND data_retention_until < ?
                AND opted_out = 0
            """, (now,)).fetchall()

            return [Candidate(**dict(row)) for row in rows]


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
