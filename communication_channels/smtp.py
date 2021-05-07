from .base_channel import CommunicationChannel
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class SmtpChannel(CommunicationChannel):
    def __init__(self, config) -> None:
        if "server" in config and config["server"]:
            self.server = config["server"]
        else:
            raise ValueError("Invalid server provided, aborting")
        if "port" in config and config["port"]:
            self.port = config["port"]
        else:
            self.port = 587
        if "send_starttls" in config and config["send_starttls"]:
            self.starttls = config["send_starttls"]
        else:
            self.starttls = False
        if "username" in config and config["username"]:
            self.username = config["username"]
        else:
            raise ValueError("Invalid username provided, aborting")
        if "password" in config and config["password"]:
            self.password = config["password"]
        else:
            raise ValueError("Invalid password provided, aborting")
        if "from_mail" in config and config["from_mail"]:
            self.from_mail = config["from_mail"]
        else:
            raise ValueError("Invalid from_mail provided, aborting")
        if "to_mail" in config and config["to_mail"]:
            self.to_mail = config["to_mail"]
        else:
            raise ValueError("Invalid to_mail provided, aborting")
        super().__init__()

    def send_message(self, message, source_sensor=None) -> None:
        mime_message = MIMEMultipart()
        mime_message["From"] = self.from_mail
        mime_message["To"] = self.to_mail
        mime_message["Subject"] = "SimpleServerMon {} alert".format(source_sensor)
        mime_message.attach(MIMEText(message, "plain"))
        try:
            server = smtplib.SMTP(host=self.server, port=self.port)
            server.ehlo()
            if self.starttls:
                server.starttls()
            server.login(self.username, self.password)
            server.sendmail(self.from_mail, self.to_mail, mime_message.as_string())
            server.quit()
        except Exception as e:
            logging.error(
                "An error occurred while sending mails via {}: {}".format(
                    self.server, str(e)
                )
            )
