#!/usr/bin/env python3
"""
Send consent request emails to candidates

Usage:
    python scripts/send_consent_emails.py 10  # Send to max 10 candidates
    python scripts/send_consent_emails.py all # Send to all candidates without consent
"""

import sys
import os
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import requests
from jinja2 import Template
from src.candidate_manager import CandidateManager
from src.config import settings
from loguru import logger


def generate_consent_link(candidate_id: int, email: str) -> str:
    """
    Generate secure consent link for candidate

    Args:
        candidate_id: Candidate's ID
        email: Candidate's email

    Returns:
        str: Consent URL
    """
    try:
        response = requests.post(
            f"{settings.public_url}/gdpr/consent/send-link",
            json={
                "candidate_id": candidate_id,
                "email": email,
                "validity_days": 7
            }
        )

        if response.ok:
            data = response.json()
            return data["consent_url"]
        else:
            logger.error(f"API error: {response.text}")
            return None

    except Exception as e:
        logger.error(f"Error generating consent link: {e}")
        return None


def render_email_template(candidate, consent_url: str) -> str:
    """
    Render email template with candidate data

    Args:
        candidate: Candidate object
        consent_url: Generated consent URL

    Returns:
        str: Rendered email body
    """
    # Load template
    template_path = 'docs/templates/email_initial_consent_request.md'

    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()

    template = Template(template_content)

    # Render with data
    email_body = template.render(
        CANDIDATE_NAME=candidate.name,
        COMPANY_NAME=settings.company_name,
        CONSENT_LINK=consent_url,
        JOB_BENEFITS=settings.job_benefits,
        PRIVACY_POLICY_URL=settings.privacy_policy_url,
        CONTACT_EMAIL=settings.contact_email,
        CONTACT_PHONE=settings.contact_phone,
        RECRUITER_NAME="Recruiting Team",
        COMPANY_WEBSITE=settings.public_url,
        COMPANY_ADDRESS="",  # TODO: Add to settings
        COMPANY_CITY="",  # TODO: Add to settings
        CURRENT_DATE=datetime.now().strftime("%d.%m.%Y")
    )

    return email_body


def send_email(to_email: str, subject: str, body: str) -> bool:
    """
    Send email via SMTP

    Args:
        to_email: Recipient email
        subject: Email subject
        body: Email body (plain text)

    Returns:
        bool: Success status
    """
    # TODO: Configure SMTP settings in .env
    SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USER = os.getenv('SMTP_USER', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    SMTP_FROM = os.getenv('SMTP_FROM', settings.contact_email)

    if not SMTP_USER or not SMTP_PASSWORD:
        logger.error("SMTP credentials not configured. Set SMTP_USER and SMTP_PASSWORD in .env")
        return False

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = SMTP_FROM
        msg['To'] = to_email

        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)

        logger.info(f"Email sent to {to_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False


def send_consent_email_to_candidate(candidate_id: int) -> bool:
    """
    Send consent request email to a specific candidate

    Args:
        candidate_id: Candidate's ID

    Returns:
        bool: Success status
    """
    manager = CandidateManager()
    candidate = manager.get_candidate(candidate_id=candidate_id)

    if not candidate:
        logger.error(f"Candidate {candidate_id} not found")
        return False

    if not candidate.email:
        logger.error(f"Candidate {candidate_id} has no email address")
        return False

    # Check if consent already given
    if manager.has_valid_consent(candidate_id):
        logger.info(f"Candidate {candidate_id} already has valid consent - skipping")
        return False

    logger.info(f"Processing candidate {candidate_id}: {candidate.name} ({candidate.email})")

    # Generate consent link
    consent_url = generate_consent_link(candidate_id, candidate.email)

    if not consent_url:
        logger.error(f"Failed to generate consent link for candidate {candidate_id}")
        return False

    logger.info(f"Consent link generated: {consent_url}")

    # Render email template
    email_body = render_email_template(candidate, consent_url)

    # Send email
    subject = f"Einwilligung erforderlich: Karrieremöglichkeiten | {settings.company_name}"

    success = send_email(candidate.email, subject, email_body)

    if success:
        logger.info(f"✅ Consent email sent to {candidate.name} ({candidate.email})")
    else:
        logger.error(f"❌ Failed to send email to {candidate.name}")

    return success


def send_bulk_consent_emails(max_candidates: int):
    """
    Send consent emails to all candidates without consent

    Args:
        max_candidates: Maximum number of candidates to process
    """
    manager = CandidateManager()

    # Get all candidates without consent
    with manager._get_connection() as conn:
        if max_candidates == -1:
            # All candidates
            rows = conn.execute("""
                SELECT id, name, email
                FROM candidates
                WHERE (consent_given = 0 OR consent_given IS NULL)
                AND email IS NOT NULL
                AND email != ''
                AND (opted_out = 0 OR opted_out IS NULL)
                ORDER BY created_at DESC
            """).fetchall()
        else:
            # Limited number
            rows = conn.execute("""
                SELECT id, name, email
                FROM candidates
                WHERE (consent_given = 0 OR consent_given IS NULL)
                AND email IS NOT NULL
                AND email != ''
                AND (opted_out = 0 OR opted_out IS NULL)
                ORDER BY created_at DESC
                LIMIT ?
            """, (max_candidates,)).fetchall()

    candidates = [dict(row) for row in rows]

    if not candidates:
        print("\n✓ No candidates found that need consent emails!")
        return

    print(f"\n📧 Sending consent emails to {len(candidates)} candidates...")
    print("=" * 60)

    success_count = 0
    failed_count = 0

    for i, candidate in enumerate(candidates, 1):
        print(f"\n[{i}/{len(candidates)}] Processing: {candidate['name']}")

        if send_consent_email_to_candidate(candidate['id']):
            success_count += 1
        else:
            failed_count += 1

        # Delay between emails to avoid spam filters
        if i < len(candidates):  # Don't delay after last email
            print("Waiting 2 seconds before next email...")
            time.sleep(2)

    print("\n" + "=" * 60)
    print(f"\n✅ Successfully sent: {success_count}/{len(candidates)} emails")
    if failed_count > 0:
        print(f"❌ Failed: {failed_count}/{len(candidates)} emails")


def main():
    """Main entry point"""

    print("\n" + "=" * 60)
    print("📧 Consent Email Sender")
    print("=" * 60)

    if len(sys.argv) < 2:
        print("""
Usage:
    python scripts/send_consent_emails.py 10    # Send to max 10 candidates
    python scripts/send_consent_emails.py all   # Send to all candidates
    python scripts/send_consent_emails.py <id>  # Send to specific candidate ID

Examples:
    python scripts/send_consent_emails.py 5
    python scripts/send_consent_emails.py all
    python scripts/send_consent_emails.py 123
        """)
        return

    arg = sys.argv[1]

    if arg == "all":
        print("\nSending to ALL candidates without consent...")
        confirm = input("Are you sure? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Cancelled.")
            return
        send_bulk_consent_emails(max_candidates=-1)

    elif arg.isdigit():
        # Could be max count or specific ID
        num = int(arg)

        # Check if it's a valid candidate ID
        manager = CandidateManager()
        candidate = manager.get_candidate(candidate_id=num)

        if candidate:
            # Send to specific candidate
            print(f"\nSending to specific candidate: {candidate.name}")
            send_consent_email_to_candidate(num)
        else:
            # Treat as max count
            print(f"\nSending to max {num} candidates...")
            send_bulk_consent_emails(max_candidates=num)

    else:
        print(f"Invalid argument: {arg}")
        print("Use a number or 'all'")


if __name__ == "__main__":
    main()
