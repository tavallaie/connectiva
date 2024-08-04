# tests/test_file_protocol.py

import unittest
import os
import shutil
import logging
import threading
from connectiva.connectiva import Connectiva
from connectiva.message import Message


class TestFileProtocolWithConnectiva(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_dir = "test_messages"
        cls.endpoint = f"file://{os.path.abspath(cls.test_dir)}"  # Use file:// scheme

        # Ensure the directory is clean before starting
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)
        os.makedirs(cls.test_dir)

        cls.connectiva = Connectiva(
            log=True,
            log_level="DEBUG",
            endpoint=cls.endpoint,
            protocol="File",  # Specify protocol directly
            directory=cls.test_dir,  # Ensure directory is passed correctly
            prefix="msg_",
            processed_prefix="processed_"
        )

        # Log the setup process
        cls.logger = logging.getLogger('TestFileProtocolWithConnectiva')
        cls.logger.info("Test setup complete. Test directory created.")

    @classmethod
    def tearDownClass(cls):
        # Clean up the test directory after all tests
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)
        cls.logger.info("Test teardown complete. Test directory removed.")

    def test_send_message(self):
        """
        Test sending a message and ensure the file is created correctly.
        """
        message = Message(action="send", data={"key": "value"})
        result = self.connectiva.send(message)
        self.assertIn("status", result)
        self.assertEqual(result["status"], "file_written")

        # Check if a file was created
        files = [f for f in os.listdir(self.test_dir) if f.startswith("msg_")]
        self.assertTrue(len(files) > 0, "No files created by send method.")

    def test_receive_message(self):
        """
        Test receiving a message and ensure the content matches the sent data.
        """
        # Create a test message file
        message_data = {"key": "value"}
        message = Message(action="send", data=message_data)
        self.connectiva.send(message)

        received_message = self.connectiva.receive()
        self.assertEqual(received_message.data, message_data, "Received data should match sent message.")

    def test_receive_no_message(self):
        """
        Test receiving when no message is available and ensure proper error handling.
        """
        # Ensure directory is empty before the test
        files = os.listdir(self.test_dir)
        for f in files:
            os.remove(os.path.join(self.test_dir, f))

        received_message = self.connectiva.receive()
        self.assertEqual(received_message.action, "error", "Action should be 'error' when no message is found.")

    def test_concurrent_access(self):
        """
        Test concurrent access to ensure that multiple receivers can process messages
        without conflicts. This test will simulate concurrent access by using multiple threads.
        """
        def receiver(connectiva, results, index):
            message = connectiva.receive()
            if message.action != "error":  # Only store successful results
                results[index] = message.data

        # Create multiple message files
        for _ in range(5):
            self.connectiva.send(Message(action="send", data={"content": "Hello!"}))

        results = [None] * 5
        threads = []

        # Start multiple receiver threads
        for i in range(5):
            thread = threading.Thread(target=receiver, args=(self.connectiva, results, i))
            thread.start()
            threads.append(thread)

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

        # Filter out None results
        filtered_results = [result for result in results if result is not None]

        # Verify that each message was processed exactly once
        expected_results = [{"content": "Hello!"}] * len(filtered_results)
        self.assertEqual(filtered_results, expected_results, "Each receiver should get the correct message content.")

    def test_locking_mechanism(self):
        """
        Test the file locking mechanism by attempting concurrent writes and reads
        """
        def write_message(connectiva, message_data):
            message = Message(action="send", data=message_data)
            connectiva.send(message)

        # Write a message to the file
        message_data_1 = {"content": "Test Lock"}
        message_data_2 = {"content": "Hello!"}

        thread_1 = threading.Thread(target=write_message, args=(self.connectiva, message_data_1))
        thread_2 = threading.Thread(target=write_message, args=(self.connectiva, message_data_2))

        thread_1.start()
        thread_2.start()

        thread_1.join()
        thread_2.join()

        # Ensure both messages are read correctly
        received_messages = []
        while True:
            received_message = self.connectiva.receive()
            if received_message.action == "error":
                break
            received_messages.append(received_message.data)

        # Verify that both messages are in the received list
        expected_results = [message_data_1, message_data_2]
        for expected in expected_results:
            self.assertIn(expected, received_messages, "Locking mechanism failed; message not read correctly.")


if __name__ == "__main__":
    unittest.main()

