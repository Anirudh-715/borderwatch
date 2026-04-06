import os
import smtplib
from email.message import EmailMessage
import threading

def _send_email_async(subject, body):
    sender_email = 'projectsoftware715@gmail.com'
    receiver_email = 'anirudh.varshney715@gmail.com'
    password = 'dxbslitxpzliynis'
    smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))


    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg.set_content(body)

    try:
        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                server.login(sender_email, password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, password)
                server.send_message(msg)
        print(f"Admin notification email sent successfully for '{subject}'.")
    except Exception as e:
        print(f"Failed to send admin notification email: {e}")


def send_admin_notification(incident_type, location, severity, description, officer_username):
    """
    Sends an email to the admin with the details of the reported incident.
    (Synchronous execution to ensure WSGI workers don't kill the thread in production)
    """
    subject = f"BorderWatch Alert: New {severity} Severity Incident Reported"
    body = f"""A new incident has been reported by Officer {officer_username}.

Details:
- Type: {incident_type}
- Severity: {severity}
- Location: {location}
- Description: {description}

Please log in to the BorderWatch system to view more details.
"""

    # Run synchronously to guarantee delivery in Gunicorn/Render deployments
    _send_email_async(subject, body)
