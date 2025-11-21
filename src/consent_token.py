"""
Secure token generation and validation for consent links
"""

import secrets
import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional, Dict
import sqlite3
from loguru import logger


class ConsentTokenManager:
    """Manages secure tokens for consent links"""

    def __init__(self, db_path: str = "./data/candidates.db"):
        self.db_path = db_path
        self._init_token_table()

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_token_table(self):
        """Initialize consent_tokens table"""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS consent_tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    token TEXT UNIQUE NOT NULL,
                    candidate_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    used BOOLEAN DEFAULT 0,
                    used_at TIMESTAMP,
                    ip_address TEXT,
                    user_agent TEXT,
                    FOREIGN KEY (candidate_id) REFERENCES candidates (id)
                )
            """)

            # Create index for faster token lookups
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_consent_tokens_token
                ON consent_tokens(token)
            """)

            conn.commit()
            logger.info("Consent tokens table initialized")

    def generate_token(
        self,
        candidate_id: int,
        validity_days: int = 7
    ) -> str:
        """
        Generate a secure consent token

        Args:
            candidate_id: The candidate's ID
            validity_days: Number of days the token is valid (default: 7)

        Returns:
            str: The generated token
        """
        # Generate secure random token (64 characters)
        token = secrets.token_urlsafe(48)

        # Calculate expiration
        expires_at = datetime.now() + timedelta(days=validity_days)

        with self._get_connection() as conn:
            # Invalidate any existing unused tokens for this candidate
            conn.execute("""
                UPDATE consent_tokens
                SET used = 1, used_at = CURRENT_TIMESTAMP
                WHERE candidate_id = ? AND used = 0
            """, (candidate_id,))

            # Insert new token
            conn.execute("""
                INSERT INTO consent_tokens (token, candidate_id, expires_at)
                VALUES (?, ?, ?)
            """, (token, candidate_id, expires_at.isoformat()))

            conn.commit()

        logger.info(f"Generated consent token for candidate {candidate_id}, expires: {expires_at}")
        return token

    def validate_token(self, token: str) -> Optional[Dict]:
        """
        Validate a consent token

        Args:
            token: The token to validate

        Returns:
            Optional[Dict]: Token info if valid, None if invalid/expired
        """
        with self._get_connection() as conn:
            row = conn.execute("""
                SELECT
                    id,
                    token,
                    candidate_id,
                    created_at,
                    expires_at,
                    used,
                    used_at
                FROM consent_tokens
                WHERE token = ?
            """, (token,)).fetchone()

            if not row:
                logger.warning(f"Token not found: {token[:10]}...")
                return None

            token_info = dict(row)

            # Check if already used
            if token_info['used']:
                logger.warning(f"Token already used: {token[:10]}... at {token_info['used_at']}")
                return None

            # Check if expired
            expires_at = datetime.fromisoformat(token_info['expires_at'])
            if datetime.now() > expires_at:
                logger.warning(f"Token expired: {token[:10]}... at {expires_at}")
                return None

            logger.info(f"Token validated successfully for candidate {token_info['candidate_id']}")
            return token_info

    def mark_token_used(
        self,
        token: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> bool:
        """
        Mark a token as used

        Args:
            token: The token to mark as used
            ip_address: IP address of the user (for audit trail)
            user_agent: User agent of the browser (for audit trail)

        Returns:
            bool: Success status
        """
        with self._get_connection() as conn:
            conn.execute("""
                UPDATE consent_tokens
                SET used = 1,
                    used_at = CURRENT_TIMESTAMP,
                    ip_address = ?,
                    user_agent = ?
                WHERE token = ?
            """, (ip_address, user_agent, token))

            conn.commit()

            logger.info(f"Token marked as used: {token[:10]}... from IP {ip_address}")
            return True

    def cleanup_expired_tokens(self, days_old: int = 30) -> int:
        """
        Delete expired tokens older than specified days

        Args:
            days_old: Delete tokens older than this many days (default: 30)

        Returns:
            int: Number of deleted tokens
        """
        cutoff_date = datetime.now() - timedelta(days=days_old)

        with self._get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM consent_tokens
                WHERE expires_at < ?
            """, (cutoff_date.isoformat(),))

            deleted_count = cursor.rowcount
            conn.commit()

            logger.info(f"Cleaned up {deleted_count} expired tokens older than {days_old} days")
            return deleted_count

    def get_token_stats(self) -> Dict:
        """
        Get statistics about consent tokens

        Returns:
            Dict: Token statistics
        """
        with self._get_connection() as conn:
            stats = {}

            # Total tokens
            stats['total_tokens'] = conn.execute(
                "SELECT COUNT(*) as count FROM consent_tokens"
            ).fetchone()['count']

            # Unused tokens
            stats['unused_tokens'] = conn.execute(
                "SELECT COUNT(*) as count FROM consent_tokens WHERE used = 0"
            ).fetchone()['count']

            # Used tokens
            stats['used_tokens'] = conn.execute(
                "SELECT COUNT(*) as count FROM consent_tokens WHERE used = 1"
            ).fetchone()['count']

            # Expired tokens
            now = datetime.now().isoformat()
            stats['expired_tokens'] = conn.execute(
                "SELECT COUNT(*) as count FROM consent_tokens WHERE expires_at < ? AND used = 0",
                (now,)
            ).fetchone()['count']

            return stats


# Example usage
if __name__ == "__main__":
    manager = ConsentTokenManager()

    # Generate token for candidate 1
    token = manager.generate_token(candidate_id=1, validity_days=7)
    print(f"Generated token: {token}")

    # Validate token
    token_info = manager.validate_token(token)
    if token_info:
        print(f"Token valid for candidate: {token_info['candidate_id']}")

        # Mark as used
        manager.mark_token_used(token, ip_address="192.168.1.1", user_agent="Mozilla/5.0")
        print("Token marked as used")

        # Try to validate again (should fail)
        if not manager.validate_token(token):
            print("Token no longer valid (already used)")

    # Get stats
    stats = manager.get_token_stats()
    print(f"\nToken Statistics: {stats}")
