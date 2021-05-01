import logging
from .base_sensors import ServerMonSensor
import time
import re
from datetime import datetime, timedelta


class SshdAccessSensor(ServerMonSensor):
    POLL_INTERVAL = 1
    DEFAULT_DURATION = 30
    DEFAULT_AMOUNT = 5
    DEFAULT_RENOTIFY_TIME = 5

    LOOK_OUT_FOR = [
        "(?<=Disconnected from invalid user )(\S+)( )([0-9\.]+)( port )([0-9]+)",
        "(?<=Connection closed by invalid user )(\S+)( )([0-9\.]+)( port )([0-9]+)",
    ]

    def __init__(self, channels, config) -> None:
        if "log_file" in config.keys():
            self.log_file = config["log_file"]
        else:
            self.log_file = "/var/log/auth.log"
        if "duration" in config.keys():
            self.duration = int(config["duration"])
        else:
            self.duration = self.DEFAULT_DURATION
        if "amount" in config.keys():
            self.amount = int(config["amount"])
        else:
            self.amount = self.DEFAULT_AMOUNT
        if "renotify_time" in config.keys():
            self.renotify_time = int(config["renotify_time"])
        else:
            self.renotify_time = self.DEFAULT_RENOTIFY_TIME
        self.suspects = {}
        self.sleep_until = datetime.now() - timedelta(days=1)
        super().__init__(channels, config)

    def do_sensor_logic(self) -> None:
        with open(self.log_file, "r") as log_handle:
            lines = self._follow_log(log_handle)
            for line in lines:
                current = datetime.now()
                if current < self.sleep_until:
                    continue
                # clean up old messages
                old_date = current - timedelta(seconds=self.duration)
                for previous_suspect_time in list(self.suspects.keys()):
                    if previous_suspect_time < old_date:
                        self.suspects.pop(previous_suspect_time)
                # check new messages
                for sshd_log_message in self.LOOK_OUT_FOR:
                    found = re.findall(sshd_log_message, line)
                    if found:
                        logging.warning(
                            "Had a suspect that tried to log in using user {}. IP: {}".format(
                                found[0][0], found[0][2]
                            )
                        )
                        self.suspects[datetime.now()] = (found[0][0], found[0][2])
                if len(self.suspects.keys()) > self.amount:
                    items = []
                    for entry in self.suspects.values():
                        items.append(
                            "IP {} tried to log in as {}".format(entry[1], entry[0])
                        )
                    self.send_message(
                        "Had {amount} of login attempts exceeding threshold of {thr}:\n{items}".format(
                            amount=len(self.suspects.keys()),
                            thr=self.amount,
                            items="\n".join(items),
                        )
                    )
                    self.suspects.clear()
                    self.sleep_until = datetime.now() + timedelta(
                        minutes=self.renotify_time
                    )

    def _follow_log(self, log_file_handle):
        log_file_handle.seek(0, 2)
        while True:
            line = log_file_handle.readline()
            if not line:
                time.sleep(self.POLL_INTERVAL)
                continue
            yield line
