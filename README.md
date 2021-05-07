# Simple Server Monitor

This project aims to provide a simple solution for monitoring server systems. It is designed to be sleek and easy to use and does not aim to compete with advanced monitoring software - especially not with software that is designed to monitor entire IT landscapes. Use it for your small home servers and lab environments, not for the mission critical servers of your multi-billion unicorn.

## Installation

Before running the script, create a *config.json* using the provided template (additional details about the available config values can be found in the [configuration file](#configuration) section).

Once the configuration file is created, the script can be executed directly by
1. (Once) Installing the dependencies using `python -m pip install -r requirements.txt`
1. Running `python simple_server_mon.py`

Alternatively, the *install.sh* script can be used on Linux to set up a new venv in the current directory and install a systemd service.

1. (Run once) `./install.sh`
1. `systemctl start simple_server_mon.service`

The service is automatically enabled and will be run again after a reboot. The current status can be queried using the regular systemd means, i.e

`systemctl status simple_server_mon.service`

## Components

The project is centered around two main types of components. The first type is the *communication channels* which are responsible for delivering the notifications to the configured recipients, and the second one is the *sensors* which do the actual monitoring. 

### Communication channels

Communication channels are used to send information about events, i.e. the means by which the script will inform about anomalies picked up by the sensors. Currently the following channels are supported:

| Name | Description |
| ----------- | ----------- |
| Telegram | A Telegram bot implementation that will send notifications to any channel into which it is invited |
| SMTP | Sends notifications via email |

All communication channels *must* inherit from *base_channel.CommunicationChannel* and implement the *send_message()* method.

### Sensors

Sensors are the components which perform the actual monitoring. They are grouped into two categories: Regular and timer based sensors.

| Name | Type | Description |
| ----------- | ---- | ----------- |
| Diskspace | Timer | Monitors the amount of free space per partition |
| Free memory | Timer | Monitors the amount of free RAM |
| SSHD Access | Regular | Monitors failed SSH login attempts |

## Configuration

The configuration is based on JSON and has two main structuring elements corresponding to the two component types *Communication channel* and *Sensor*. A template file is provided too and can be used as basis for creating custom configurations.

### Communication channels

| Name | Parameter | Description | Default |
| ----------- | ----------- | ----------- | ----------- |
| telegram | chat_id | The ID of the chat into which the bot will post messages |  |
| telegram | token | The bot token provided by [BotFather](https://t.me/botfather) |  |
| smtp | server | The server address of the SMTP server |  |
| smtp | port | The port to be used for the SMTP communication | 587 |
| smtp | send_starttls | Whether STARTTLS shall be used | False |
| smtp | username | The username for the authentication towards the SMTP server |  |
| smtp | password | The password for the authentication towards the SMTP server |  |
| smtp | from_mail | The sender's mail address |  |
| smtp | to_mail | The recipients mail address |  |

### Sensors
| Name | Parameter | Description | Default |
| ----------- | ----------- | ----------- | ----------- |
| diskspace | update_interval | The intervall for checking the amount of free space, in seconds | 10 |
| diskspace | threshold | The disk usage threshold above which a notification will be sent | 20 |
| diskspace | excluded_partitions | A list of partitions (i.e. mount points) which is excluded from being monitored |  |
| free_memory | update_interval | The intervall for checking the amount of free memory, in seconds | 10 |
| free_memory | threshold | The used RAM threshold above which a notification will be sent | 20 |
| sshd_access | log_file | The path to the SSHD logfile that shall be monitored | /var/log/auth.log |
| sshd_access | duration | The amount of seconds for which consecutive logging attempts will be monitored. In other words: The intervall in which the *amount* of login attempts needs to be exceeded for the notification to be sent |  |
| sshd_access | amount | The amount of login attempts that needs to be exceeded per *duration* seconds for the notification to be snet |  |
| sshd_access | renotify_time | Duration between notifications about new connection attempt amount exceeding the configured threshold (in minutes) |  |

## Logging

Two environment variables can be used to control the log level and whether a log file will be written:

| Variable | Description | Default |
| ----------- | ----------- | ----------- |
| LOG_LEVEL | The log level | INFO |
| LOG_FILE | The path to the log file. If none is provided, no log file will be written by the script directly, i.e. only stdout / stderr and syslog based logs will be used |  |

Additionally, if installed via the *install.sh* script in a Linux environment all logging will be handled by systemd. To query the logs in this mode use

`journalctl -xeu simple_server_mon.service`