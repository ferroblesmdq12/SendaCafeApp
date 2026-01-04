# services/alerts.py

from core.config import get_env_var
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def send_stock_critical_email(producto: str, stock_actual: int, stock_minimo: int) -> int:
    """
    Envía un email de alerta por stock crítico usando SendGrid.

    Requiere variables:
      - SENDGRID_API_KEY
      - ALERT_EMAIL_TO      (puede ser "a@x.com,b@y.com")
      - ALERT_EMAIL_FROM
    Devuelve status_code (202 = aceptado).
    """
    api_key = get_env_var("SENDGRID_API_KEY")
    to_email = get_env_var("ALERT_EMAIL_TO")
    from_email = get_env_var("ALERT_EMAIL_FROM")

    if not api_key or not to_email or not from_email:
        raise RuntimeError("Faltan variables SENDGRID_API_KEY / ALERT_EMAIL_TO / ALERT_EMAIL_FROM")

    # Soportar múltiples destinatarios separados por coma
    to_emails = [e.strip() for e in str(to_email).split(",") if e.strip()]

    subject = f"[Senda Café] Stock crítico: {producto}"
    body = (
        "Alerta de stock crítico\n\n"
        f"Producto: {producto}\n"
        f"Stock actual: {stock_actual}\n"
        f"Stock mínimo: {stock_minimo}\n\n"
        "Acción sugerida: reponer mercadería."
    )

    message = Mail(
        from_email=from_email,
        to_emails=to_emails,
        subject=subject,
        plain_text_content=body,
    )

    sg = SendGridAPIClient(api_key)

    try:
        resp = sg.send(message)

        # Logs útiles (ver en Streamlit Cloud -> Manage app -> Logs)
        print("SENDGRID_STATUS:", resp.status_code)
        print("SENDGRID_BODY:", resp.body)
        print("SENDGRID_HEADERS:", resp.headers)

        return int(resp.status_code)

    except Exception as e:
        # SendGrid suele exponer estos campos en la excepción
        status = getattr(e, "status_code", None)
        body = getattr(e, "body", None)
        headers = getattr(e, "headers", None)

        # Logs útiles (sin exponer secretos)
        print("SENDGRID_EXCEPTION_REPR:", repr(e))
        print("SENDGRID_EXCEPTION_STATUS:", status)
        print("SENDGRID_EXCEPTION_BODY:", body)
        print("SENDGRID_EXCEPTION_HEADERS:", headers)

        raise RuntimeError(f"SendGrid error: status={status}, body={body}")

## ---###