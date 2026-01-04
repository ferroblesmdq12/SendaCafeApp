# services/alerts.py

from core.config import get_env_var
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def send_stock_critical_email(producto: str, stock_actual: int, stock_minimo: int):
    api_key = get_env_var("SENDGRID_API_KEY")
    to_email = get_env_var("ALERT_EMAIL_TO")
    from_email = get_env_var("ALERT_EMAIL_FROM")

    if not api_key or not to_email or not from_email:
        raise RuntimeError("Faltan variables SENDGRID_API_KEY / ALERT_EMAIL_TO / ALERT_EMAIL_FROM")

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
        plain_text_content=body
    )

    sg = SendGridAPIClient(api_key)

    try:
        resp = sg.send(message)
        # Esto queda visible en Logs
        print("SENDGRID_STATUS:", resp.status_code)
        print("SENDGRID_BODY:", resp.body)
        return resp.status_code

    except Exception as e:
        # Esto queda visible en Logs
        print("SENDGRID_EXCEPTION:", repr(e))
        print("SENDGRID_EXCEPTION_STATUS:", getattr(e, "status_code", None))
        print("SENDGRID_EXCEPTION_BODY:", getattr(e, "body", None))
        print("SENDGRID_EXCEPTION_HEADERS:", getattr(e, "headers", None))
        raise RuntimeError(f"SendGrid error al enviar alerta: {repr(e)}")
