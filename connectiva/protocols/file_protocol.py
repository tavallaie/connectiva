# connectiva/protocols/file_protocol.py

import os
import json
import fcntl
import logging
from uuid import uuid4
from typing import Dict, Any
from connectiva import CommunicationMethod, Message

class FileProtocol(CommunicationMethod):
    """
    File sharing communication class with atomic file naming and processing.
    """

    def __init__(self, **kwargs):
        self.directory = kwargs.get("directory", ".")
        self.prefix = kwargs.get("prefix", "msg_")
        self.processed_prefix = kwargs.get("processed_", "processed_")
        self.logger = logging.getLogger(self.__class__.__name__)

        # Ensure the directory exists
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
            self.logger.debug(f"Directory {self.directory} created.")

    def connect(self):
        self.logger.info(f"Accessing directory at {self.directory}...")

    def _generate_filename(self) -> str:
        """
        Generate a unique filename for each message.
        """
        return f"{self.prefix}{uuid4().hex}.json"

    def _lock_file(self, file):
        """
        Lock the file to ensure exclusive access.
        """
        self.logger.debug(f"Locking file {file.name}...")
        try:
            fcntl.flock(file, fcntl.LOCK_EX)
            self.logger.debug(f"File {file.name} locked successfully!")
        except Exception as e:
            self.logger.error(f"Failed to lock file: {e}")
            raise

    def _unlock_file(self, file):
        """
        Unlock the file to release access.
        """
        self.logger.debug(f"Unlocking file {file.name}...")
        try:
            fcntl.flock(file, fcntl.LOCK_UN)
            self.logger.debug(f"File {file.name} unlocked successfully!")
        except Exception as e:
            self.logger.error(f"Failed to unlock file: {e}")
            raise

    def send(self, message: Message) -> Dict[str, Any]:
        """
        Write a message to a uniquely named file.

        :param message: Message object containing data to be written.
        :return: Dictionary indicating the status of the file operation.
        """
        filename = self._generate_filename()
        file_path = os.path.join(self.directory, filename)
        self.logger.info(f"Writing message to file {file_path}...")

        try:
            with open(file_path, 'w') as file:
                self._lock_file(file)
                json.dump(message.__dict__, file)
                self._unlock_file(file)
            self.logger.info("Message written successfully!")
            return {"status": "file_written", "file_path": file_path}
        except Exception as e:
            self.logger.error(f"Failed to write message: {e}")
            return {"error": str(e)}

    def receive(self) -> Message:
        """
        Read and process the oldest unprocessed message file.

        :return: Message object containing data read from the file.
        """
        self.logger.info(f"Scanning directory {self.directory} for messages...")
        files = sorted(
            [f for f in os.listdir(self.directory) if f.startswith(self.prefix)],
            key=lambda f: os.path.getctime(os.path.join(self.directory, f))
        )

        if not files:
            self.logger.info("No new messages found.")
            return Message(action="error", data={}, metadata={"error": "No message found"})

        for filename in files:
            file_path = os.path.join(self.directory, filename)
            try:
                # Lock the file and rename it to indicate processing
                with open(file_path, 'r+') as file:
                    self._lock_file(file)

                    # Check if the file has already been processed
                    if file_path.startswith(self.processed_prefix):
                        self._unlock_file(file)
                        continue

                    new_file_path = os.path.join(self.directory, self.processed_prefix + filename)
                    os.rename(file_path, new_file_path)
                    self.logger.info(f"Renamed file to {new_file_path} for processing.")

                    # Read the message
                    file.seek(0)  # Reset file pointer to the beginning
                    data = json.load(file)
                    self._unlock_file(file)
                    self.logger.info("Message read successfully!")
                    return Message(**data)
            except Exception as e:
                self.logger.error(f"Failed to read message: {e}")
                return Message(action="error", data={}, metadata={"error": str(e)})

        return Message(action="error", data={}, metadata={"error": "No message found"})

    def disconnect(self):
        self.logger.info("Closing directory access...")
