import json
import os
import urllib.error
import urllib.request


SENDGRID_API_URL = "https://api.sendgrid.com/v3/mail/send"


def parse_recipients(value):
    return [email.strip() for email in str(value or "").split(",") if email.strip()]


def is_email_enabled():
    return bool(
        os.environ.get("SENDGRID_API_KEY")
        and os.environ.get("SENDGRID_FROM_EMAIL")
        and os.environ.get("NOTIFY_TO_EMAIL")
    )


def build_email_html(numero_guia, estado, ai_audit, blob_url, sheet_url):
    review_text = "Sí" if ai_audit.get("reviewApplied") else "No"
    steps_count = ai_audit.get("stepsCount", "")

    return f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.5; color: #111;">
      <h2>Guía procesada correctamente</h2>

      <p>Se procesó una nueva guía y fue escrita en Google Sheets.</p>

      <ul>
        <li><strong>Número de guía:</strong> {numero_guia}</li>
        <li><strong>Estado:</strong> {estado}</li>
        <li><strong>Pasos IA:</strong> {steps_count}</li>
        <li><strong>Revisión IA aplicada:</strong> {review_text}</li>
      </ul>

      <p>
        <a href="{sheet_url}">Ver Google Sheets</a>
      </p>

      <p>
        <a href="{blob_url}">Ver foto original</a>
      </p>
    </div>
    """


def email_error_payload(error):
    payload = {
        "type": error.__class__.__name__,
        "message": str(error) or repr(error),
    }

    if isinstance(error, urllib.error.HTTPError):
        payload["status"] = error.code
        payload["reason"] = error.reason
        try:
            body = error.read().decode("utf-8")
            payload["body"] = body
            payload["parsed"] = json.loads(body) if body else None
        except Exception:
            pass

    return payload


def send_guia_processed_email(numero_guia, estado, ai_audit, blob_url):
    if not is_email_enabled():
        return {
            "sent": False,
            "skipped": True,
            "reason": "missing_email_env",
            "provider": "sendgrid",
        }

    api_key = os.environ["SENDGRID_API_KEY"]
    sender_email = os.environ["SENDGRID_FROM_EMAIL"]
    sender_name = os.environ.get("SENDGRID_FROM_NAME", "Guias Helice")
    recipients = parse_recipients(os.environ["NOTIFY_TO_EMAIL"])
    sheet_url = os.environ.get("GOOGLE_SHEET_URL", "")

    if not recipients:
        return {
            "sent": False,
            "skipped": True,
            "reason": "empty_recipients",
            "provider": "sendgrid",
        }

    subject = f"Guía procesada OK - Nº {numero_guia}"
    html = build_email_html(
        numero_guia=numero_guia,
        estado=estado,
        ai_audit=ai_audit or {},
        blob_url=blob_url or "",
        sheet_url=sheet_url or "",
    )

    payload = {
        "personalizations": [
            {
                "to": [{"email": email} for email in recipients]
            }
        ],
        "from": {
            "email": sender_email,
            "name": sender_name,
        },
        "subject": subject,
        "content": [
            {
                "type": "text/html",
                "value": html,
            }
        ],
    }

    request = urllib.request.Request(
        SENDGRID_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request) as response:
            body = response.read().decode("utf-8")
            return {
                "sent": True,
                "skipped": False,
                "provider": "sendgrid",
                "to": recipients,
                "from": sender_email,
                "status": response.status,
                "response": json.loads(body) if body else None,
            }
    except Exception as error:
        return {
            "sent": False,
            "skipped": False,
            "provider": "sendgrid",
            "to": recipients,
            "from": sender_email,
            "error": email_error_payload(error),
        }
