import json
import os
import urllib.request


RESEND_API_URL = "https://api.resend.com/emails"


def parse_recipients(value):
    return [email.strip() for email in str(value or "").split(",") if email.strip()]


def is_email_enabled():
    return bool(
        os.environ.get("RESEND_API_KEY")
        and os.environ.get("ALERT_EMAIL_FROM")
        and os.environ.get("ALERT_EMAIL_TO")
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


def send_guia_processed_email(numero_guia, estado, ai_audit, blob_url):
    if not is_email_enabled():
        return {
            "sent": False,
            "skipped": True,
            "reason": "missing_email_env",
        }

    api_key = os.environ["RESEND_API_KEY"]
    sender = os.environ["ALERT_EMAIL_FROM"]
    recipients = parse_recipients(os.environ["ALERT_EMAIL_TO"])
    sheet_url = os.environ.get("GOOGLE_SHEET_URL", "")

    subject = f"Guía procesada OK - Nº {numero_guia}"
    html = build_email_html(
        numero_guia=numero_guia,
        estado=estado,
        ai_audit=ai_audit or {},
        blob_url=blob_url or "",
        sheet_url=sheet_url or "",
    )

    payload = {
        "from": sender,
        "to": recipients,
        "subject": subject,
        "html": html,
    }

    request = urllib.request.Request(
        RESEND_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with urllib.request.urlopen(request) as response:
        body = response.read().decode("utf-8")
        return {
            "sent": True,
            "skipped": False,
            "response": json.loads(body) if body else None,
        }
