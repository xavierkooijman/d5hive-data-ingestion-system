import smtplib
import logging
from email.mime.text import MIMEText
from utils.common import resolve_secret

logger = logging.getLogger(__name__)


def send_email(email_config, html_content, env=None):
    """Send an email with the given HTML content using the provided email configuration.
    Args:
        email_config (dict): A dictionary containing email configuration details such as:
            - from: The sender's email address
            - password: The sender's email password
            - api_key: API key for email service (if using a service like Resend)
            - subject: The subject of the email
            - recipients: A list of recipient email addresses
        html_content (str): The HTML content of the email.
        env (str, optional): The environment in which to send the email. Defaults to None.

    Returns:
        None
    """

    email_config = dict(email_config)

    if "password" in email_config:
        email_config["password"] = resolve_secret(email_config["password"])

    if "api_key" in email_config:
        email_config["api_key"] = resolve_secret(email_config["api_key"])

    subject = email_config.get("subject", "Pipeline Report")
    recipients = email_config.get("recipients", [])

    if env == "render":
        import resend

        resend.api_key = email_config.get("api_key")

        try:
            result = resend.Emails.send({
                "from": email_config.get("from"),
                "to": "xavierkooijman@gmail.com",
                "subject": subject,
                "html": html_content,
            })

            logger.info("Email sent successfully!")
            logger.info(f"Email ID: {result['id']}")

        except Exception as e:
            logger.error(f"Error sending email: {e}")
            raise

    else:
        SMTP_SERVER = "smtp.gmail.com"
        SMTP_PORT = 587

        try:
            msg = MIMEText(html_content, "html")
            msg["Subject"] = subject
            msg["From"] = email_config.get("from")
            msg["To"] = ", ".join(recipients)

            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(
                    email_config.get("from"),
                    email_config.get("password")
                )
                server.sendmail(
                    email_config.get("from"),
                    recipients,
                    msg.as_string()
                )

            logger.info("Email sent successfully!")

        except Exception as e:
            logger.error(f"Error sending email: {e}")
            raise
