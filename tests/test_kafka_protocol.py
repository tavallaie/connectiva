import unittest
import time
import logging
from connectiva import Connectiva, Message


class TestKafkaWithConnectiva(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Set up logging configuration
        cls.log_file = "connectiva_kafka_test.log"  # Log file path
        cls.logger = logging.getLogger("ConnectivaKafkaTest")

        # Initialize Connectiva with Kafka configuration
        cls.connectiva = Connectiva(
            endpoint='kafka://localhost:9092',  # Correct Kafka endpoint format
            topic='test_topic',
            group_id='test_group',
            log=True,  # Enable logging to stdout
            log_file=cls.log_file,  # Enable logging to file
            log_level="DEBUG"
        )
        cls.connectiva.connect()
        cls.logger.info("Connected to Kafka using Connectiva")

    @classmethod
    def tearDownClass(cls):
        # Disconnect after all tests
        cls.connectiva.disconnect()
        cls.logger.info("Disconnected from Kafka using Connectiva")

    def test_send_and_receive_message(self):
        self.logger.debug("Testing send_and_receive_message")

        # Send a message to the Kafka topic
        sent_message = Message(action="send", data={"key": "value"})
        send_result = self.connectiva.send(sent_message)
        self.logger.debug(f"Send result: {send_result}")
        self.assertEqual(send_result["status"], "sent", "Message send status should be 'sent'")

        # Allow some time for the message to be available
        time.sleep(2)

        # Receive the message from the Kafka topic
        received_message = self.connectiva.receive()
        self.logger.debug(f"Received message: {received_message}")

        # Validate the received message
        self.assertEqual(received_message.action, "receive", "Received action should be 'receive'")
        self.assertEqual(received_message.data, sent_message.__dict__, "Received data should match sent message")

    def test_receive_no_message(self):
        self.logger.debug("Testing receive_no_message")

        # Ensure there are no messages to consume
        time.sleep(2)  # Wait for any stray messages to be consumed
        self.connectiva.consumer.seek_to_end()

        # Attempt to receive a message when no messages are expected
        received_message = self.connectiva.receive()
        self.logger.debug(f"Receive result: {received_message}")

        # Check that an error action is returned when no message is found
        self.assertEqual(received_message.action, "error", "Action should be 'error' when no message is found")
        self.assertIn("No message found", received_message.metadata.get("error", ""), "Error metadata should indicate no message found")


if __name__ == '__main__':
    unittest.main()
