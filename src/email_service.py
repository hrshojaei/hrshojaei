"""
E-Mail-Service für Versand von Einwilligungsanfragen
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from src.config import settings


class EmailService:
    """Service zum Versenden von E-Mails"""

    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password
        self.from_email = settings.get_from_email()
        self.from_name = settings.get_from_name()

    def send_consent_request(self, to_email: str, token: str,
                            purpose: str, company_name: Optional[str] = None) -> bool:
        """
        Sendet Einwilligungsanfrage per E-Mail

        Args:
            to_email: Empfänger E-Mail
            token: Eindeutiger Token für Einwilligung
            purpose: Zweck der Einwilligung
            company_name: Optional: Firmenname

        Returns:
            True wenn erfolgreich gesendet
        """
        if not company_name:
            company_name = settings.company_name

        # Erstelle Einwilligungs-Link
        consent_link = f"{settings.public_url}/consent/{token}"

        # E-Mail-Inhalt
        subject = f"Einwilligung zur Datenverarbeitung - {company_name}"

        html_content = self._generate_consent_email_html(
            to_email=to_email,
            consent_link=consent_link,
            purpose=purpose,
            company_name=company_name
        )

        text_content = self._generate_consent_email_text(
            to_email=to_email,
            consent_link=consent_link,
            purpose=purpose,
            company_name=company_name
        )

        return self._send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )

    def _generate_consent_email_html(self, to_email: str, consent_link: str,
                                     purpose: str, company_name: str) -> str:
        """Generiert HTML-Inhalt für Einwilligungs-E-Mail"""
        return f"""
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background-color: #0066cc;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 5px 5px 0 0;
        }}
        .content {{
            background-color: #f9f9f9;
            padding: 30px;
            border: 1px solid #ddd;
        }}
        .button {{
            display: inline-block;
            background-color: #0066cc;
            color: white;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 5px;
            margin: 20px 0;
            font-weight: bold;
        }}
        .button:hover {{
            background-color: #0052a3;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            font-size: 12px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{company_name}</h1>
        <p>Einwilligung zur Datenverarbeitung</p>
    </div>

    <div class="content">
        <p>Sehr geehrte Damen und Herren,</p>

        <p>
            wir möchten Sie um Ihre Einwilligung zur Verarbeitung Ihrer personenbezogenen
            Daten bitten. Diese Einwilligung benötigen wir für folgenden Zweck:
        </p>

        <p><strong>{purpose}</strong></p>

        <p>
            Ihre Daten werden ausschließlich für den angegebenen Zweck verwendet und
            gemäß den Bestimmungen der DSGVO verarbeitet.
        </p>

        <p>
            <strong>Ihre Rechte:</strong><br>
            - Sie können Ihre Einwilligung jederzeit widerrufen<br>
            - Sie haben ein Recht auf Auskunft über Ihre gespeicherten Daten<br>
            - Sie haben ein Recht auf Löschung Ihrer Daten<br>
            - Sie haben ein Recht auf Datenübertragbarkeit
        </p>

        <p style="text-align: center;">
            <a href="{consent_link}" class="button">
                Jetzt Einwilligung erteilen
            </a>
        </p>

        <p style="font-size: 12px; color: #666;">
            Alternativ können Sie folgenden Link in Ihren Browser kopieren:<br>
            <a href="{consent_link}">{consent_link}</a>
        </p>
    </div>

    <div class="footer">
        <p>
            {company_name}<br>
            E-Mail: {self.from_email}
        </p>
        <p>
            Diese E-Mail wurde an {to_email} gesendet.<br>
            Falls Sie diese E-Mail fälschlicherweise erhalten haben,
            können Sie sie einfach ignorieren.
        </p>
    </div>
</body>
</html>
        """

    def _generate_consent_email_text(self, to_email: str, consent_link: str,
                                     purpose: str, company_name: str) -> str:
        """Generiert Text-Inhalt für Einwilligungs-E-Mail (Fallback)"""
        return f"""
{company_name}
Einwilligung zur Datenverarbeitung

Sehr geehrte Damen und Herren,

wir möchten Sie um Ihre Einwilligung zur Verarbeitung Ihrer personenbezogenen
Daten bitten. Diese Einwilligung benötigen wir für folgenden Zweck:

{purpose}

Ihre Daten werden ausschließlich für den angegebenen Zweck verwendet und
gemäß den Bestimmungen der DSGVO verarbeitet.

Ihre Rechte:
- Sie können Ihre Einwilligung jederzeit widerrufen
- Sie haben ein Recht auf Auskunft über Ihre gespeicherten Daten
- Sie haben ein Recht auf Löschung Ihrer Daten
- Sie haben ein Recht auf Datenübertragbarkeit

Bitte klicken Sie auf folgenden Link, um Ihre Einwilligung zu erteilen:
{consent_link}

---
{company_name}
E-Mail: {self.from_email}

Diese E-Mail wurde an {to_email} gesendet.
Falls Sie diese E-Mail fälschlicherweise erhalten haben, können Sie sie einfach ignorieren.
        """

    def _send_email(self, to_email: str, subject: str,
                   html_content: str, text_content: str) -> bool:
        """
        Sendet E-Mail via SMTP

        Args:
            to_email: Empfänger
            subject: Betreff
            html_content: HTML-Inhalt
            text_content: Text-Inhalt (Fallback)

        Returns:
            True wenn erfolgreich
        """
        try:
            # Erstelle Multipart-Nachricht
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email

            # Füge Text- und HTML-Version hinzu
            part_text = MIMEText(text_content, 'plain', 'utf-8')
            part_html = MIMEText(html_content, 'html', 'utf-8')

            msg.attach(part_text)
            msg.attach(part_html)

            # Sende via SMTP
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            print(f"✓ E-Mail erfolgreich an {to_email} gesendet")
            return True

        except Exception as e:
            print(f"✗ Fehler beim E-Mail-Versand an {to_email}: {str(e)}")
            return False
