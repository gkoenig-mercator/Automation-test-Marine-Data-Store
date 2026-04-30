import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Union

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465
REPORT_URL = (
    "https://gkoenig-mercator.github.io/"
    "Automation-test-Marine-Data-Store/generated_table/"
)

MAX_EMAIL_SIZE_BYTES = 5 * 1024 * 1024  # 25 MB


class ReportMailer:
    def __init__(
        self,
        sender: str,
        recipients: Union[str, list[str]],
        password: str | None = None,
    ) -> None:
        self.sender = sender
        self.recipients = [recipients] if isinstance(recipients, str) else recipients
        self.password: str = password or os.environ.get("EMAIL_PASSWORD") or ""

        if not self.password:
            raise ValueError(
                "No email password provided. "
                "Set EMAIL_PASSWORD env var or pass password= argument."
            )

        if not self.recipients:
            raise ValueError("At least one recipient is required.")

    def _attach_files(
        self, msg: MIMEMultipart, attachments: list[str]
    ) -> MIMEMultipart:
        for filepath in attachments:
            path = Path(filepath)
            if not path.exists():
                raise FileNotFoundError(f"Attachment not found: {filepath}")
            with open(path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={path.name}")
            msg.attach(part)
        return msg

    def _check_email_size(self, msg: MIMEMultipart) -> None:
        email_size = len(msg.as_bytes())
        if email_size > MAX_EMAIL_SIZE_BYTES:
            raise ValueError(
                f"Email size ({email_size / 1024 / 1024:.2f} MB) exceeds "
                f"the maximum allowed size of "
                f"{MAX_EMAIL_SIZE_BYTES / 1024 / 1024:.0f} MB."
            )

    def send(
        self, subject: str, body: str, attachments: list[str] | None = None
    ) -> None:
        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = self.sender
        msg["To"] = ", ".join(self.recipients)
        msg.attach(MIMEText(body, "plain"))

        if attachments:
            msg = self._attach_files(msg, attachments)

        self._check_email_size(msg)

        try:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
                server.login(self.sender, self.password)
                server.send_message(msg)
            print(f"Email sent to {self.recipients}")
        except smtplib.SMTPAuthenticationError:
            raise RuntimeError("Authentication failed. Check your email and password.")
        except smtplib.SMTPException as e:
            raise RuntimeError(f"Failed to send email: {e}")

    def send_report(
        self, success: bool = False, attachments: list[str] | None = None
    ) -> None:
        if success:
            subject = "Script Complete - OK"
            body = "Your script has finished running successfully!"
        else:
            subject = "Script Complete - Issues Found"
            body = (
                "Your script has finished running but there was an issue. "
                f"Check the report here: {REPORT_URL}"
            )
        self.send(subject=subject, body=body, attachments=attachments)
