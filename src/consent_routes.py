"""
FastAPI Routes für Consent Management
"""
from fastapi import APIRouter, Request, HTTPException, Form
from fastapi.responses import HTMLResponse
from typing import Optional
from src.consent_manager import ConsentManager
from src.email_service import EmailService
from src.config import settings

router = APIRouter(prefix="/consent", tags=["consent"])
consent_manager = ConsentManager()
email_service = EmailService()


@router.get("/{token}", response_class=HTMLResponse)
async def show_consent_form(token: str):
    """
    Zeigt Einwilligungsformular für gegebenen Token

    Args:
        token: Eindeutiger Token der Anfrage

    Returns:
        HTML-Seite mit Einwilligungsformular
    """
    # Hole Consent-Anfrage
    consent_request = consent_manager.get_consent_by_token(token)

    if not consent_request:
        return _generate_error_page("Ungültiger Link",
                                   "Dieser Einwilligungslink ist ungültig oder abgelaufen.")

    if consent_request.consent_given:
        return _generate_success_page(
            "Einwilligung bereits erteilt",
            f"Sie haben Ihre Einwilligung bereits am {consent_request.consent_timestamp} erteilt."
        )

    # Zeige Einwilligungsformular
    return _generate_consent_form(consent_request.email, token, consent_request.purpose)


@router.post("/{token}")
async def confirm_consent(token: str, request: Request, agree: str = Form(...)):
    """
    Verarbeitet Einwilligungs-Bestätigung

    Args:
        token: Token der Anfrage
        request: FastAPI Request für IP/User-Agent
        agree: Zustimmung ("yes" oder "no")

    Returns:
        HTML-Bestätigungsseite
    """
    if agree != "yes":
        return _generate_error_page(
            "Einwilligung abgelehnt",
            "Sie haben die Einwilligung zur Datenverarbeitung abgelehnt. "
            "Ihre Daten werden nicht gespeichert."
        )

    # Hole Client-Informationen für DSGVO-Nachweis
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    # Speichere Einwilligung
    success = consent_manager.confirm_consent(token, client_ip, user_agent)

    if not success:
        return _generate_error_page(
            "Fehler",
            "Diese Einwilligung wurde bereits erteilt oder der Link ist ungültig."
        )

    # Hole E-Mail für Bestätigung
    consent_request = consent_manager.get_consent_by_token(token)

    return _generate_success_page(
        "Vielen Dank!",
        f"Ihre Einwilligung wurde erfolgreich gespeichert. "
        f"Wir werden Sie unter {consent_request.email} kontaktieren."
    )


def _generate_consent_form(email: str, token: str, purpose: str) -> str:
    """Generiert HTML-Formular für Einwilligung"""
    return f"""
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Einwilligung zur Datenverarbeitung</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        .container {{
            background: white;
            border-radius: 10px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 600px;
            width: 100%;
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}
        .header p {{
            opacity: 0.9;
            font-size: 16px;
        }}
        .content {{
            padding: 40px 30px;
        }}
        .info-box {{
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 20px;
            margin-bottom: 30px;
            border-radius: 5px;
        }}
        .info-box strong {{
            display: block;
            margin-bottom: 10px;
            color: #667eea;
            font-size: 16px;
        }}
        .consent-text {{
            background: #fff;
            border: 1px solid #e0e0e0;
            padding: 25px;
            margin: 30px 0;
            border-radius: 8px;
            max-height: 400px;
            overflow-y: auto;
        }}
        .consent-text h2 {{
            color: #667eea;
            font-size: 20px;
            margin-bottom: 15px;
        }}
        .consent-text h3 {{
            color: #764ba2;
            font-size: 16px;
            margin-top: 20px;
            margin-bottom: 10px;
        }}
        .consent-text p {{
            margin-bottom: 12px;
        }}
        .consent-text ul {{
            margin-left: 20px;
            margin-bottom: 12px;
        }}
        .consent-text li {{
            margin-bottom: 8px;
        }}
        .checkbox-container {{
            display: flex;
            align-items: center;
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        .checkbox-container input[type="checkbox"] {{
            width: 20px;
            height: 20px;
            margin-right: 15px;
            cursor: pointer;
        }}
        .checkbox-container label {{
            cursor: pointer;
            font-size: 16px;
        }}
        .button-group {{
            display: flex;
            gap: 15px;
            margin-top: 30px;
        }}
        button {{
            flex: 1;
            padding: 15px 30px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        button[type="submit"] {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        button[type="submit"]:hover:not(:disabled) {{
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }}
        button[type="submit"]:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
        }}
        button[type="button"] {{
            background: #e0e0e0;
            color: #666;
        }}
        button[type="button"]:hover {{
            background: #d0d0d0;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 20px 30px;
            text-align: center;
            font-size: 12px;
            color: #666;
            border-top: 1px solid #e0e0e0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{settings.company_name}</h1>
            <p>Einwilligung zur Datenverarbeitung</p>
        </div>

        <div class="content">
            <div class="info-box">
                <strong>E-Mail-Adresse:</strong>
                {email}
            </div>

            <div class="consent-text">
                <h2>Datenschutzeinwilligung</h2>

                <p>
                    Wir, {settings.company_name}, möchten Sie gerne bezüglich beruflicher
                    Möglichkeiten kontaktieren. Hierfür benötigen wir Ihre Einwilligung zur
                    Verarbeitung Ihrer personenbezogenen Daten.
                </p>

                <h3>Zweck der Datenverarbeitung</h3>
                <p><strong>{purpose}</strong></p>
                <p>
                    Dies umfasst insbesondere die Kontaktaufnahme per E-Mail und Telefon zur
                    Information über passende Stellenangebote und karriererelevante Inhalte.
                </p>

                <h3>Welche Daten werden verarbeitet?</h3>
                <ul>
                    <li>Name und Kontaktdaten (E-Mail, Telefonnummer)</li>
                    <li>Berufliche Informationen (aktueller Arbeitgeber, Berufserfahrung)</li>
                    <li>Gesprächsnotizen und Interessensgebiete</li>
                </ul>

                <h3>Rechtsgrundlage</h3>
                <p>
                    Die Verarbeitung erfolgt auf Grundlage Ihrer Einwilligung gemäß
                    Art. 6 Abs. 1 lit. a DSGVO.
                </p>

                <h3>Ihre Rechte</h3>
                <ul>
                    <li><strong>Widerruf:</strong> Sie können Ihre Einwilligung jederzeit mit Wirkung für die Zukunft widerrufen</li>
                    <li><strong>Auskunft:</strong> Sie haben das Recht auf Auskunft über die zu Ihrer Person gespeicherten Daten</li>
                    <li><strong>Löschung:</strong> Sie können die Löschung Ihrer Daten verlangen</li>
                    <li><strong>Berichtigung:</strong> Sie können die Berichtigung unrichtiger Daten verlangen</li>
                    <li><strong>Datenübertragbarkeit:</strong> Sie haben das Recht auf Übertragung Ihrer Daten</li>
                    <li><strong>Beschwerde:</strong> Sie können sich bei einer Datenschutz-Aufsichtsbehörde beschweren</li>
                </ul>

                <h3>Kontakt</h3>
                <p>
                    Bei Fragen oder zur Ausübung Ihrer Rechte erreichen Sie uns unter:<br>
                    E-Mail: {settings.contact_email}<br>
                    Telefon: {settings.contact_phone}
                </p>

                <h3>Datenspeicherung</h3>
                <p>
                    Ihre Daten werden solange gespeichert, wie dies für die genannten Zwecke
                    erforderlich ist oder bis Sie Ihre Einwilligung widerrufen.
                </p>
            </div>

            <form method="POST" action="/consent/{token}" id="consentForm">
                <div class="checkbox-container">
                    <input type="checkbox" id="agreeCheckbox" name="agree_checkbox" required>
                    <label for="agreeCheckbox">
                        Ich habe die Datenschutzinformationen gelesen und willige in die
                        Verarbeitung meiner personenbezogenen Daten wie oben beschrieben ein.
                    </label>
                </div>

                <input type="hidden" name="agree" value="no" id="agreeValue">

                <div class="button-group">
                    <button type="button" onclick="window.close()">Ablehnen</button>
                    <button type="submit" id="submitBtn" disabled>Einwilligung erteilen</button>
                </div>
            </form>
        </div>

        <div class="footer">
            <p>
                {settings.company_name} | {settings.contact_email}<br>
                Diese Einwilligung wurde angefordert für: {email}
            </p>
        </div>
    </div>

    <script>
        const checkbox = document.getElementById('agreeCheckbox');
        const submitBtn = document.getElementById('submitBtn');
        const agreeValue = document.getElementById('agreeValue');

        checkbox.addEventListener('change', function() {{
            submitBtn.disabled = !this.checked;
            agreeValue.value = this.checked ? 'yes' : 'no';
        }});

        document.getElementById('consentForm').addEventListener('submit', function(e) {{
            if (!checkbox.checked) {{
                e.preventDefault();
                alert('Bitte bestätigen Sie die Datenschutzeinwilligung.');
            }}
        }});
    </script>
</body>
</html>
    """


def _generate_success_page(title: str, message: str) -> str:
    """Generiert Erfolgsseite"""
    return f"""
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        .container {{
            background: white;
            border-radius: 10px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 500px;
            width: 100%;
            padding: 60px 40px;
            text-align: center;
        }}
        .icon {{
            width: 80px;
            height: 80px;
            background: #4caf50;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 30px;
        }}
        .icon svg {{
            width: 50px;
            height: 50px;
            fill: white;
        }}
        h1 {{
            color: #333;
            font-size: 32px;
            margin-bottom: 20px;
        }}
        p {{
            color: #666;
            font-size: 18px;
            line-height: 1.6;
            margin-bottom: 30px;
        }}
        button {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="icon">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
            </svg>
        </div>
        <h1>{title}</h1>
        <p>{message}</p>
        <button onclick="window.close()">Fenster schließen</button>
    </div>
</body>
</html>
    """


def _generate_error_page(title: str, message: str) -> str:
    """Generiert Fehlerseite"""
    return f"""
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        .container {{
            background: white;
            border-radius: 10px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 500px;
            width: 100%;
            padding: 60px 40px;
            text-align: center;
        }}
        .icon {{
            width: 80px;
            height: 80px;
            background: #f44336;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 30px;
        }}
        .icon svg {{
            width: 50px;
            height: 50px;
            fill: white;
        }}
        h1 {{
            color: #333;
            font-size: 32px;
            margin-bottom: 20px;
        }}
        p {{
            color: #666;
            font-size: 18px;
            line-height: 1.6;
            margin-bottom: 30px;
        }}
        button {{
            background: #e0e0e0;
            color: #666;
            border: none;
            padding: 15px 40px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        button:hover {{
            background: #d0d0d0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="icon">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
            </svg>
        </div>
        <h1>{title}</h1>
        <p>{message}</p>
        <button onclick="window.close()">Fenster schließen</button>
    </div>
</body>
</html>
    """


# API Routes für programmatischen Zugriff
@router.post("/api/send")
async def send_consent_request(email: str, purpose: str = "Kontaktaufnahme und Datenspeicherung"):
    """
    API-Endpunkt zum Versenden einer Einwilligungsanfrage

    Args:
        email: E-Mail-Adresse des Empfängers
        purpose: Zweck der Einwilligung

    Returns:
        JSON mit Status und Token
    """
    try:
        # Erstelle Consent-Anfrage
        consent_request = consent_manager.create_consent_request(email, purpose)

        # Sende E-Mail
        success = email_service.send_consent_request(
            to_email=email,
            token=consent_request.token,
            purpose=purpose
        )

        if not success:
            raise HTTPException(status_code=500, detail="E-Mail konnte nicht gesendet werden")

        return {
            "success": True,
            "email": email,
            "token": consent_request.token,
            "message": "Einwilligungsanfrage wurde gesendet"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/status/{email}")
async def get_consent_status(email: str):
    """
    API-Endpunkt zum Prüfen des Einwilligungsstatus

    Args:
        email: E-Mail-Adresse

    Returns:
        JSON mit allen Einwilligungen für diese E-Mail
    """
    requests = consent_manager.get_consent_status(email)
    has_consent = consent_manager.has_valid_consent(email)

    return {
        "email": email,
        "has_valid_consent": has_consent,
        "total_requests": len(requests),
        "requests": [
            {
                "id": req.id,
                "purpose": req.purpose,
                "created_at": req.created_at,
                "consent_given": req.consent_given,
                "consent_timestamp": req.consent_timestamp
            }
            for req in requests
        ]
    }
