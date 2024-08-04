import unittest
import time
import logging
from connectiva import Connectiva, Message


class TestKafkaWithConnectiva(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Set up logging configuration
        cls.logger = logging.getLogger("ConnectivaKafkaTest")

        # Initialize Connectiva with Kafka configuration
        cls.connectiva = Connectiva(
            endpoint='kafka://localhost:9092',
            topic='test_topic',
            group_id='test_group',
            log=True,  # Enable logging to stdout
            log_level="DEBUG"
        )
        cls.connectiva.connect()
        cls.logger.info("Connected to Kafka using Connectiva")

    @classmethod
    def tearDownClass(cls):
        # Disconnect after all tests
        cls.connectiva.disconnect()
        cls.logger.info("Disconnected from Kafka using Connectiva")

    def test_send_message(self):
        self.logger.debug("Testing send_message")
        message = Message(action="send", data={"key": "value"})
        result = self.connectiva.send(message)
        self.logger.debug(f"Send result: {result}")
        self.assertEqual(result["status"], "sent", "Message send status should be 'sent'")

    def test_receive_message(self):
        self.logger.debug("Testing receive_message")
        sent_message = Message(action="send", data={"key": "value"})
        self.connectiva.send(sent_message)

        time.sleep(1)  # Allow some time for the message to be available

        received_message = self.connectiva.receive()
        self.logger.debug(f"Received message: {received_message}")
        self.assertEqual(received_message.action, "receive", "Received action should be 'receive'")
        self.assertEqual(received_message.data, sent_message.__dict__, "Received data should match sent message")

    def test_receive_no_message(self):
        self.logger.debug("Testing receive_no_message")
        time.sleep(1)  # Allow time for the consumer to poll
        received_message = self.connectiva.receive()
        self.logger.debug(f"Receive result: {received_message}")
        self.assertEqual(received_message.action, "error", "Action should be 'error' when no message is found")
        self.assertIn("No message found", received_message.metadata.get("error", ""), "Error metadata should indicate no message found")


if __name__ == '__main__':
    unittest.main()
