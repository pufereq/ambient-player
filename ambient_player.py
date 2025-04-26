#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import datetime
import logging
import random
import os
from typing import Any
import playsound3
import time
import yaml


class AmbientPlayer:
    def __init__(self):
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.info("Initializing AmbientPlayer")

        self.data_dir: str = os.path.join(os.path.dirname(__file__), "data")
        self.media_dir: str = os.path.join(self.data_dir, "media")

        self.playlist: list[dict[str, Any]] = []

        self.min_break_seconds: int = 0  # seconds
        self.max_break_seconds: int = 0  # seconds

        self.time_categories: list[dict[str, str]] = []

        self.load_config()
        self.load_playlist()
        self.logger.info("AmbientPlayer initialized")

    def load_config(self):
        self.logger.info("Loading config")

        config_path = os.path.join(self.data_dir, "config.yaml")
        if not os.path.exists(config_path):
            self.logger.error(f"Config file not found: {config_path}")
            return

        with open(config_path, "r") as file_:
            config = yaml.safe_load(file_)
            if not config:
                self.logger.error("Config file is empty or invalid")
                return

            self.time_categories = config.get("time_categories", {})
            if not self.time_categories:
                self.logger.error("No time categories found in config")
                return

            if "min_break_seconds" not in config:
                self.logger.warning(
                    f"min_break_seconds not found in config, using default: {self.min_break_seconds} seconds"
                )
                config["min_break_seconds"] = self.min_break_seconds
            self.min_break_seconds = config["min_break_seconds"]

            if "max_break_seconds" not in config:
                self.logger.warning(
                    f"max_break_seconds not found in config, using default: {self.max_break_seconds} seconds"
                )
                config["max_break_seconds"] = self.max_break_seconds
            self.max_break_seconds = config["max_break_seconds"]

        self.logger.info(f"Loaded config: {config}")

    def parse_time(self, time_str: str) -> datetime.time:
        self.logger.debug(f"Parsing time string: {time_str}")
        try:
            time_obj = datetime.datetime.strptime(time_str, "%H:%M").time()
            self.logger.debug(f"Parsed time object: {time_obj}")
            return time_obj
        except ValueError as e:
            self.logger.error(f"Error parsing time string '{time_str}': {e}")
            raise ValueError(f"Invalid time format: {time_str}") from e

    def load_playlist(self):
        self.logger.info("Loading playlist")

        for category in self.time_categories:
            name: str = category.get("name", "")
            if not name:
                self.logger.error("Category name is missing")
                continue

            start_time: datetime.time = self.parse_time(category.get("start_time", ""))
            end_time: datetime.time = self.parse_time(category.get("end_time", ""))

            media_files: list[str] = []
            media_path = os.path.join(self.media_dir, name)
            if not os.path.exists(media_path):
                self.logger.error(f"Media path not found: {media_path}")
                continue

            for file_name in os.listdir(media_path):
                if file_name.endswith(".mp3") or file_name.endswith(".wav"):
                    media_files.append(os.path.join(media_path, file_name))

            if not media_files:
                self.logger.warning(f"No media files found in {media_path}")
                continue

            self.playlist.append(
                {
                    "name": name,
                    "start_time": start_time,
                    "end_time": end_time,
                    "media_files": media_files,
                }
            )
        self.logger.info(f"Loaded playlist: {self.playlist}")

    def play(self):
        self.logger.info("Starting playback")
        while True:
            now = datetime.datetime.now().time()
            scheduled_playlists = [
                category
                for category in self.playlist
                if category["start_time"] <= now <= category["end_time"]
            ]

            if not scheduled_playlists:
                self.logger.info("No scheduled playlists found, waiting for next cycle")
                time.sleep(60)
                continue

            self.logger.info(
                "Scheduled playlists: "
                + ", ".join(playlist["name"] for playlist in scheduled_playlists)
            )

            category = random.choice(scheduled_playlists)
            media_files = category["media_files"]
            self.logger.info(f"Playing category: {category['name']}")

            media_file = random.choice(media_files)
            self.logger.info(f"Playing media file: {media_file}")

            try:
                playsound3.playsound(media_file)
            except Exception as e:
                self.logger.error(f"Error playing media file '{media_file}': {e}")
                continue
            self.logger.info("Playback finished, taking a break")

            break_time = random.randint(self.min_break_seconds, self.max_break_seconds)

            for i in range(break_time):
                if i % 5 == 0:
                    formatted_time = datetime.timedelta(seconds=i)
                    self.logger.info(
                        f"Break time: {formatted_time} / {datetime.timedelta(seconds=break_time)}"
                    )
                time.sleep(1)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    player = AmbientPlayer()
    player.play()
