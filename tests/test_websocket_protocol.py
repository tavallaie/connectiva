# tests/test_websocket_protocol.py

import unittest
import logging
import threading
import nest_asyncio
import asyncio
from connectiva import Connectiva, Message

# Apply the nest_asyncio patch
nest_asyncio.apply()

class TestWebSocketProtocolWithConnectiva(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Set up logging
        logging.basicConfig(level=logging.DEBUG)

        # Start the WebSocket server using Connectiva
        cls.server = Connectiva(
            endpoint="ws://localhost:8765",
            mode="server",
            log=True
        )
        cls.server_thread = threading.Thread(target=cls.server.connect)
        cls.server_thread.start()

        # Start the WebSocket client using Connectiva
        cls.client = Connectiva(
            endpoint="ws://localhost:8765",
            mode="client",
            log=True
        )
        cls.client.connect()

    @classmethod
    def tearDownClass(cls):
        # Disconnect both client and server
        cls.client.disconnect()
        cls.server.disconnect()
        cls.server_thread.join()

    def test_send_receive(self):
        # Test sending and receiving messages
        message = Message(action="send", data={"content": "Hello WebSocket!"})
        response = self.client.send(message)
        self.assertEqual(response["status"], "sent", "Message should be sent successfully.")

        received_message = self.client.receive()
        # Check for the 'received' key in the echoed message
        self.assertEqual(received_message.data["data"]["received"], message.data["content"], "Received message should match sent message.")

    def test_server_client_communication(self):
        # Test communication between server and client
        message = Message(action="send", data={"content": "Server-Client Test"})
        response = self.client.send(message)
        self.assertEqual(response["status"], "sent", "Message should be sent successfully.")

        received_message = self.client.receive()
        # Check for the 'received' key in the echoed message
        self.assertEqual(received_message.data["data"]["received"], message.data["content"], "Server should echo the message back to the client.")


if __name__ == "__main__":
    unittest.main()
