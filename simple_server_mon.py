import logging
import os
import json
import sys
import importlib


class SimpleServerMon:
    mandatory_params = set(["messaging_channels", "sensors"])

    def __init__(self) -> None:
        log_level = (
            logging.INFO if os.getenv("LOG_LEVEL") is None else os.getenv("LOG_LEVEL")
        )
        handlers = [logging.StreamHandler()]
        if os.getenv("LOG_FILE") is not None:
            handlers.append(logging.FileHandler(os.getenv("LOG_FILE")))
        logging.basicConfig(
            format="%(asctime)s | %(filename)21s:%(lineno)3d | %(levelname)7s | %(message)s",
            level=log_level,
            datefmt="%Y/%m/%d %H:%M:%S",
            handlers=handlers,
        )
        logging.info("Starting SimpleServerMon")
        try:
            with open("config.json", "r") as config_file:
                self.config = json.load(config_file)
        except Exception as e:
            logging.error("An error occurred while opening config.json: {}".format(e))
            sys.exit(1)
        self._check_config()
        self.communication_channels = []
        self._parse_messaging_channels()

    def _parse_messaging_channels(self) -> None:
        for channel_definition in self.config["messaging_channels"]:
            key = next(iter(channel_definition.keys()))
            try:
                sensor_module = importlib.import_module(
                    "communication_channels.{}".format(key)
                )
                class_ = getattr(sensor_module, "{}Channel".format(key.capitalize()))
                self.communication_channels.append(
                    class_(
                        next(iter(channel_definition.values())),
                    )
                )
            except ModuleNotFoundError as e:
                logging.warning(
                    "Unknown communication channel {} found. Your config might be incorrect. Error: {}".format(
                        key, e
                    )
                )

    def _check_config(self) -> None:
        """Check whether the configuration contains all mandatory elements and exit if it does not"""
        flattened_config = set(self._flatten_keys(self.config))
        missing = [
            param
            for param in SimpleServerMon.mandatory_params
            if param not in flattened_config
        ]
        if len(missing) > 0:
            logging.error(
                "The following mandatory parameters are missing from the config: {}".format(
                    ",".join(missing)
                )
            )
            sys.exit(2)

    def _flatten_keys(self, dictionary) -> list:
        """Flattens the keys all layers of the given dictionary (including all sub-dictionatries and lists) to a single list

        Args:
            dictionary (dict): The dictionary to be flattened

        Returns:
            list: The list of keys in the initial dictionary
        """
        result = []
        result.extend(dictionary.keys())
        for val in dictionary.values():
            if isinstance(val, dict):
                result.extend(self._flatten_keys(val))
            if isinstance(val, list):
                for sub_item in val:
                    if isinstance(sub_item, dict):
                        result.extend(self._flatten_keys(sub_item))
        return result

    def _snake_to_camel(self, snake_string) -> str:
        components = snake_string.split("_")
        return "".join(x.capitalize() for x in components)

    def run_daemons(self) -> None:
        for sensor_definition in self.config["sensors"]:
            key = next(iter(sensor_definition.keys()))
            try:
                sensor_module = importlib.import_module("sensors.{}".format(key))
                class_ = getattr(
                    sensor_module, "{}Sensor".format(self._snake_to_camel(key))
                )
                class_(
                    self.communication_channels,
                    next(iter(sensor_definition.values())),
                )
            except ModuleNotFoundError as e:
                logging.warning(
                    "Unknown sensor {} found. Your config might be incorrect. Error: {}".format(
                        key, e
                    )
                )


if __name__ == "__main__":
    instance = SimpleServerMon()
    instance.run_daemons()