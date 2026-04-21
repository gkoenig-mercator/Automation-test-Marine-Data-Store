import smtplib
from email.mime.text import MIMEText
import os

sender = "gkoenigmercatorocean@gmail.com"
recipient = "gkoenig@mercator-ocean.fr"
password = os.environ["EMAIL_PASSWORD"]

msg = MIMEText("Your script has finished running!")
msg["Subject"] = "Script Complete"
msg["From"] = sender
msg["To"] = recipient

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    server.login(sender, password)
    server.send_message(msg)

print("Email sent!")