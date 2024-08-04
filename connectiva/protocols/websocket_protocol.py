import asyncio
import websockets
import json
import logging
from typing import Dict, Any
from connectiva import CommunicationMethod, Message

class WebSocketProtocol(CommunicationMethod):
    """
    WebSocket protocol that can operate as both a server and client.
    """

    def __init__(self, **kwargs):
        self.mode = kwargs.get("mode", "client")  # "client" or "server"
        self.endpoint = kwargs.get("endpoint", "ws://localhost:8765")
        self.logger = logging.getLogger(self.__class__.__name__)
        self.websocket = None
        self.server = None

    async def start_server(self):
        """
        Starts the WebSocket server.
        """
        host, port = self._parse_websocket_url(self.endpoint)
        self.logger.info(f"Starting WebSocket server on {self.endpoint}...")
        try:
            self.server = await websockets.serve(self.handler, host, port)
            self.logger.info("WebSocket server started.")
            await self.server.wait_closed()
        except Exception as e:
            self.logger.error(f"Failed to start WebSocket server: {e}")

    async def connect_async(self):
        """
        Connects to a WebSocket server.
        """
        self.logger.info(f"Connecting to WebSocket at {self.endpoint}...")
        try:
            self.websocket = await websockets.connect(self.endpoint)
            self.logger.info("Connected to WebSocket!")
        except Exception as e:
            self.logger.error(f"Failed to connect to WebSocket: {e}")

    async def handler(self, websocket, path):
        """
        Handles incoming WebSocket connections.
        """
        self.logger.info("Client connected.")
        try:
            async for message in websocket:
                self.logger.info(f"Received message: {message}")
                response = json.dumps({"action": "response", "data": {"received": message}})
                await websocket.send(response)
        except websockets.exceptions.ConnectionClosed as e:
            self.logger.info(f"Client disconnected: {e}")

    def connect(self):
        """
        Starts the server or connects as a client based on the mode.
        """
        if self.mode == "server":
            asyncio.get_event_loop().run_until_complete(self.start_server())
        elif self.mode == "client":
            asyncio.get_event_loop().run_until_complete(self.connect_async())
        else:
            self.logger.error("Invalid mode specified. Use 'client' or 'server'.")

    async def send_async(self, message: Message) -> Dict[str, Any]:
        """
        Sends a message via WebSocket.
        """
        self.logger.info("Sending message via WebSocket...")
        try:
            await self.websocket.send(json.dumps(message.__dict__))
            self.logger.info("Message sent successfully!")
            return {"status": "sent"}
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            return {"error": str(e)}

    def send(self, message: Message) -> Dict[str, Any]:
        """
        Unified method to send a message.
        """
        if self.mode == "client":
            return asyncio.get_event_loop().run_until_complete(self.send_async(message))
        else:
            self.logger.error("Sending directly from server mode is not supported.")
            return {"error": "Invalid operation in server mode"}

    async def receive_async(self) -> Message:
        """
        Receives a message via WebSocket.
        """
        self.logger.info("Receiving message via WebSocket...")
        try:
            message = await self.websocket.recv()
            self.logger.info("Message received successfully!")
            return Message(action="receive", data=json.loads(message))
        except Exception as e:
            self.logger.error(f"Failed to receive message: {e}")
            return Message(action="error", data={}, metadata={"error": str(e)})

    def receive(self) -> Message:
        """
        Unified method to receive a message.
        """
        if self.mode == "client":
            return asyncio.get_event_loop().run_until_complete(self.receive_async())
        else:
            self.logger.error("Receiving directly from server mode is not supported.")
            return Message(action="error", data={}, metadata={"error": "Invalid operation in server mode"})

    async def disconnect_async(self):
        """
        Disconnects the WebSocket connection.
        """
        self.logger.info("Disconnecting from WebSocket...")
        if self.websocket:
            await self.websocket.close()

    def disconnect(self):
        """
        Unified method to disconnect.
        """
        if self.mode == "client":
            asyncio.get_event_loop().run_until_complete(self.disconnect_async())
        elif self.mode == "server" and self.server:
            self.server.close()
            self.logger.info("WebSocket server stopped.")
        else:
            self.logger.error("No active connection to disconnect.")

    @staticmethod
    def _parse_websocket_url(endpoint: str):
        """
        Parse the WebSocket URL to extract the host and port.
        """
        try:
            if endpoint.startswith("ws://") or endpoint.startswith("wss://"):
                address = endpoint.split("//")[1]
                host, port = address.split(":")
                return host, int(port)
            raise ValueError("Invalid WebSocket URL format")
        except Exception as e:
            raise ValueError(f"Error parsing WebSocket URL: {e}")
