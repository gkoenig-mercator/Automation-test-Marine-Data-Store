import os
import smtplib
from email.mime.text import MIMEText


def sending_mail():
    sender = "gkoenigmercatorocean@gmail.com"
    recipient = "gkoenig@mercator-ocean.fr"
    password = os.environ["EMAIL_PASSWORD"]
    link = (
        "https://gkoenig-mercator.github.io/"
        "Automation-test-Marine-Data-Store/generated_table/"
    )
    msg = MIMEText(
        "Your script has finished running! "
        "But there was an issue, "
        "you should check the page: "
        f"{link} "
        "to know more about this!"
    )
    msg["Subject"] = "Script Complete"
    msg["From"] = sender
    msg["To"] = recipient

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.send_message(msg)

    print("Email sent!")
