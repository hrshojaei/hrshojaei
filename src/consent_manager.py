"""
Consent Manager - Verwaltet Datenschutz-Einwilligungen per E-Mail
"""
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, List


@dataclass
class ConsentRequest:
    """Repräsentiert eine Einwilligungsanfrage"""
    id: Optional[int]
    email: str
    token: str
    purpose: str  # Zweck der Einwilligung
    created_at: str
    consent_given: bool
    consent_timestamp: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]


class ConsentManager:
    """Verwaltet Datenschutz-Einwilligungen"""

    def __init__(self, db_path: str = "data/consent.db"):
        self.db_path = db_path
        self._ensure_database()

    def _ensure_database(self):
        """Erstellt Datenbank und Tabellen falls nicht vorhanden"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS consent_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                token TEXT UNIQUE NOT NULL,
                purpose TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                consent_given BOOLEAN DEFAULT 0,
                consent_timestamp TIMESTAMP NULL,
                ip_address TEXT NULL,
                user_agent TEXT NULL
            )
        """)

        # Index für schnellere Token-Suche
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_token
            ON consent_requests(token)
        """)

        # Index für E-Mail-Suche
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_email
            ON consent_requests(email)
        """)

        conn.commit()
        conn.close()

    def create_consent_request(self, email: str, purpose: str = "Datenspeicherung und -verarbeitung") -> ConsentRequest:
        """
        Erstellt eine neue Einwilligungsanfrage

        Args:
            email: E-Mail-Adresse des Empfängers
            purpose: Zweck der Einwilligung

        Returns:
            ConsentRequest-Objekt mit generiertem Token
        """
        token = str(uuid.uuid4())

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO consent_requests (email, token, purpose, consent_given)
            VALUES (?, ?, ?, 0)
        """, (email, token, purpose))

        request_id = cursor.lastrowid
        conn.commit()

        # Hole erstellte Anfrage
        cursor.execute("""
            SELECT id, email, token, purpose, created_at, consent_given,
                   consent_timestamp, ip_address, user_agent
            FROM consent_requests WHERE id = ?
        """, (request_id,))

        row = cursor.fetchone()
        conn.close()

        return ConsentRequest(
            id=row[0],
            email=row[1],
            token=row[2],
            purpose=row[3],
            created_at=row[4],
            consent_given=bool(row[5]),
            consent_timestamp=row[6],
            ip_address=row[7],
            user_agent=row[8]
        )

    def get_consent_by_token(self, token: str) -> Optional[ConsentRequest]:
        """
        Findet Einwilligungsanfrage anhand des Tokens

        Args:
            token: Eindeutiger Token

        Returns:
            ConsentRequest oder None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, email, token, purpose, created_at, consent_given,
                   consent_timestamp, ip_address, user_agent
            FROM consent_requests WHERE token = ?
        """, (token,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return ConsentRequest(
            id=row[0],
            email=row[1],
            token=row[2],
            purpose=row[3],
            created_at=row[4],
            consent_given=bool(row[5]),
            consent_timestamp=row[6],
            ip_address=row[7],
            user_agent=row[8]
        )

    def confirm_consent(self, token: str, ip_address: Optional[str] = None,
                       user_agent: Optional[str] = None) -> bool:
        """
        Markiert Einwilligung als erteilt

        Args:
            token: Token der Anfrage
            ip_address: IP-Adresse des Nutzers (für Nachweiszwecke)
            user_agent: Browser User-Agent

        Returns:
            True wenn erfolgreich, False wenn Token nicht gefunden
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE consent_requests
            SET consent_given = 1,
                consent_timestamp = ?,
                ip_address = ?,
                user_agent = ?
            WHERE token = ? AND consent_given = 0
        """, (datetime.now().isoformat(), ip_address, user_agent, token))

        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()

        return rows_affected > 0

    def get_consent_status(self, email: str) -> List[ConsentRequest]:
        """
        Holt alle Einwilligungsanfragen für eine E-Mail-Adresse

        Args:
            email: E-Mail-Adresse

        Returns:
            Liste von ConsentRequest-Objekten
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, email, token, purpose, created_at, consent_given,
                   consent_timestamp, ip_address, user_agent
            FROM consent_requests
            WHERE email = ?
            ORDER BY created_at DESC
        """, (email,))

        rows = cursor.fetchall()
        conn.close()

        return [
            ConsentRequest(
                id=row[0],
                email=row[1],
                token=row[2],
                purpose=row[3],
                created_at=row[4],
                consent_given=bool(row[5]),
                consent_timestamp=row[6],
                ip_address=row[7],
                user_agent=row[8]
            )
            for row in rows
        ]

    def has_valid_consent(self, email: str, purpose: Optional[str] = None) -> bool:
        """
        Prüft ob gültige Einwilligung vorhanden ist

        Args:
            email: E-Mail-Adresse
            purpose: Optional: Spezifischer Zweck

        Returns:
            True wenn gültige Einwilligung existiert
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if purpose:
            cursor.execute("""
                SELECT COUNT(*) FROM consent_requests
                WHERE email = ? AND purpose = ? AND consent_given = 1
            """, (email, purpose))
        else:
            cursor.execute("""
                SELECT COUNT(*) FROM consent_requests
                WHERE email = ? AND consent_given = 1
            """, (email,))

        count = cursor.fetchone()[0]
        conn.close()

        return count > 0
