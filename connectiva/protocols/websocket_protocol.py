# connectiva/protocols/websocket_protocol.py

import asyncio
import websockets
import json
import logging
from typing import Dict, Any, Tuple
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
        self.loop = asyncio.get_event_loop()

    def _parse_websocket_url(self) -> Tuple[str, int]:
        """
        Parse the WebSocket URL to extract the host and port.
        """
        try:
            if self.endpoint.startswith("ws://") or self.endpoint.startswith("wss://"):
                address = self.endpoint.split("//")[1]
                host, port = address.split(":")
                return host, int(port)
            raise ValueError("Invalid WebSocket URL format")
        except Exception as e:
            raise ValueError(f"Error parsing WebSocket URL: {e}")

    async def _start_server(self):
        """
        Starts the WebSocket server.
        """
        host, port = self._parse_websocket_url()
        self.logger.info(f"Starting WebSocket server on {self.endpoint}...")
        try:
            self.server = await websockets.serve(self._server_handler, host, port)
            self.logger.info("WebSocket server started.")
            await self.server.wait_closed()
        except Exception as e:
            self.logger.error(f"Failed to start WebSocket server: {e}")

    async def _connect_async(self):
        """
        Connects to a WebSocket server.
        """
        self.logger.info(f"Connecting to WebSocket at {self.endpoint}...")
        try:
            self.websocket = await websockets.connect(self.endpoint)
            self.logger.info("Connected to WebSocket!")
        except Exception as e:
            self.logger.error(f"Failed to connect to WebSocket: {e}")

    async def _server_handler(self, websocket, path):
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
            asyncio.run(self._start_server())
        elif self.mode == "client":
            asyncio.run(self._connect_async())
        else:
            self.logger.error("Invalid mode specified. Use 'client' or 'server'.")

    async def _send_async(self, message: Message) -> Dict[str, Any]:
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
            return asyncio.run(self._send_async(message))
        else:
            self.logger.error("Sending directly from server mode is not supported.")
            return {"error": "Invalid operation in server mode"}

    async def _receive_async(self) -> Message:
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
            return asyncio.run(self._receive_async())
        else:
            self.logger.error("Receiving directly from server mode is not supported.")
            return Message(action="error", data={}, metadata={"error": "Invalid operation in server mode"})

    async def _disconnect_async(self):
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
            asyncio.run(self._disconnect_async())
        elif self.mode == "server" and self.server:
            self.server.close()
            self.logger.info("WebSocket server stopped.")
        else:
            self.logger.error("No active connection to disconnect.")
