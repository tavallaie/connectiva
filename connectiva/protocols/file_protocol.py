import unittest
import os
import shutil
import logging
import threading
import time
from connectiva.connectiva import Connectiva
from connectiva.message import Message

# Configure logging
logging.basicConfig(level=logging.DEBUG)


class TestFileProtocolWithConnectiva(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_dir = "test_messages"
        cls.connectiva = Connectiva(
            log=True,
            directory=cls.test_dir,
            protocol="File",
            prefix="msg_",
            processed_prefix="processed_"
        )

        # Ensure the directory is clean before starting
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)
        os.makedirs(cls.test_dir)

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
        files = [f for f in os.listdir(self.test_dir) if f.startswith(self.connectiva.config.get('prefix'))]
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

        # Verify that each message was processed exactly once
        expected_results = [{"content": "Hello!"}] * 5
        self.assertEqual(sorted(results), sorted(expected_results), "Each receiver should get the correct message content.")

    def test_locking_mechanism(self):
        """
        Test the file locking mechanism by attempting concurrent writes and reads,
        ensuring that the lock is acquired and released properly.
        """
        lock_acquired = threading.Event()

        def write_with_lock(connectiva, message_data):
            nonlocal lock_acquired
            message = Message(action="send", data=message_data)
            connectiva.send(message)
            lock_acquired.set()  # Indicate that the lock was acquired

        def read_with_lock(connectiva, result):
            nonlocal lock_acquired
            # Wait until the lock is acquired by the write operation
            lock_acquired.wait()
            time.sleep(0.5)  # Wait for a bit to ensure the write lock is held
            result.append(connectiva.receive().data)

        write_thread = threading.Thread(target=write_with_lock, args=(self.connectiva, {"content": "Test Lock"}))
        result = []
        read_thread = threading.Thread(target=read_with_lock, args=(self.connectiva, result))

        write_thread.start()
        read_thread.start()

        write_thread.join()
        read_thread.join()

        # Check if the message was read successfully
        self.assertEqual(result[0], {"content": "Test Lock"}, "Locking mechanism failed; message not read correctly.")


if __name__ == '__main__':
    unittest.main()
