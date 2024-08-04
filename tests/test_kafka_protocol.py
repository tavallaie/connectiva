import unittest
import time
from connectiva.protocols import KafkaProtocol
from connectiva import Message

class TestKafkaProtocol(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Use a Kafka broker for testing
        cls.protocol = KafkaProtocol(
            endpoint='localhost:9092',  # Assuming Kafka is running on localhost
            topic='test_topic',
            group_id='test_group'
        )
        cls.protocol.connect()

    @classmethod
    def tearDownClass(cls):
        # Disconnect after all tests
        cls.protocol.disconnect()

    def test_send_message(self):
        # Send a message and check the response
        message = Message(action="send", data={"key": "value"})
        result = self.protocol.send(message)
        self.assertEqual(result["status"], "sent", "Message send status should be 'sent'")

    def test_receive_message(self):
        # Send a message first to ensure there's something to receive
        sent_message = Message(action="send", data={"key": "value"})
        self.protocol.send(sent_message)
        
        # Allow some time for the message to be available
        time.sleep(1)

        # Receive the message and verify contents
        received_message = self.protocol.receive()
        self.assertEqual(received_message.action, "receive", "Received action should be 'receive'")
        self.assertEqual(received_message.data, sent_message.__dict__, "Received data should match sent message")

    def test_receive_no_message(self):
        # Attempt to receive when no message is expected
        # Assume we clean the topic or use a new consumer group for this test
        # No prior send means no messages to receive
        time.sleep(1)  # Allow time for the consumer to poll
        received_message = self.protocol.receive()
        self.assertEqual(received_message.action, "error", "Action should be 'error' when no message is found")
        self.assertIn("No message found", received_message.metadata.get("error", ""), "Error metadata should indicate no message found")


if __name__ == '__main__':
    unittest.main()
