import unittest
import time
from connectiva.protocols import AMQPProtocol
from connectiva import Message

class TestAMQPProtocol(unittest.TestCase):

    def setUp(self):
        # Set up the protocol with real data
        self.protocol = AMQPProtocol(endpoint='amqp://guest:guest@localhost:5672/', queue_name='test_queue')
        self.protocol.connect()

    def tearDown(self):
        # Disconnect after each test
        self.protocol.disconnect()

    def test_connect(self):
        # Check if connection is established
        self.assertIsNotNone(self.protocol.connection)
        self.assertIsNotNone(self.protocol.channel)

    def test_send_message(self):
        # Create a message and send it
        message = Message(action="send", data={"key": "value"})
        result = self.protocol.send(message)
        self.assertEqual(result, {"status": "sent"})

    def test_receive_message(self):
        # Send a message first
        sent_message = Message(action="send", data={"key": "value"})
        self.protocol.send(sent_message)
        
        # Allow some time for message to be processed (optional)
        time.sleep(1)

        # Receive the message
        received_message = self.protocol.receive()
        
        # Check if the received message matches
        self.assertEqual(received_message.action, "receive")
        self.assertEqual(received_message.data, {"key": "value"})

    def test_receive_no_message(self):
        # Receive when no message is expected
        received_message = self.protocol.receive()
        self.assertEqual(received_message.action, "error")
        self.assertEqual(received_message.metadata, {"error": "No message found"})


if __name__ == '__main__':
    unittest.main()
