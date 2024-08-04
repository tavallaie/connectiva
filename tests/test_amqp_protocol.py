# tests/test_amqp_protocol.py

import unittest
import time
from connectiva.protocols.amqp_protocol import AMQPProtocol
from connectiva import Message


class TestAMQPProtocol(unittest.TestCase):

    def setUp(self):
        # Use a fixed endpoint for testing
        self.protocol = AMQPProtocol(endpoint='amqp://guest:guest@127.0.0.1:5672/', queue_name='test_queue')
        self.protocol.connect()

        # Ensure the queue is empty before each test
        self.clear_queue()

    def tearDown(self):
        # Ensure disconnect after each test
        self.protocol.disconnect()

    def clear_queue(self):
        # Purge the queue to ensure it's empty
        self.protocol.channel.queue_purge(queue=self.protocol.queue_name)

    def test_connect(self):
        # Verify connection is established
        self.assertIsNotNone(self.protocol.connection, "Connection should be established")
        self.assertIsNotNone(self.protocol.channel, "Channel should be created")

    def test_send_message(self):
        # Send a message and check the response
        message = Message(action="send", data={"key": "value"})
        result = self.protocol.send(message)
        self.assertEqual(result, {"status": "sent"}, "Message send status should be 'sent'")

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
        received_message = self.protocol.receive()
        self.assertEqual(received_message.action, "error", "Action should be 'error' when no message is found")
        self.assertEqual(received_message.metadata, {"error": "No message found"}, "Error metadata should indicate no message found")


if __name__ == '__main__':
    unittest.main()
