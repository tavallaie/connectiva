 # Connectiva

 **Connectiva: A Unified Microservice Communication Library**

 ---

 ## Overview

 Connectiva is a powerful and flexible Python library designed to streamline communication across diverse microservices architectures. Whether you're using REST APIs, gRPC, Kafka, WebSockets, or traditional message brokers, Connectiva provides a unified interface to handle all your communication needs effortlessly.

 ## Features

 - **Protocol Agnostic:** Automatically detects and adapts to the communication protocol being used, whether it's REST, gRPC, Kafka, RabbitMQ, WebSockets, GraphQL, or file-based communication.
 - **Ease of Use:** Leverages an intuitive, consistent API that allows you to connect, send, receive, and disconnect seamlessly across different communication methods.
 - **Extensibility:** Built with modularity in mind, allowing developers to extend or customize communication strategies as needed.
 - **Efficiency:** Utilizes efficient connection management and message handling to ensure robust performance in high-load environments.

 ## Installation

 Connectiva can be easily installed using [Poetry](https://python-poetry.org/), a dependency management tool for Python.

 ### Using Poetry

 To install Connectiva using Poetry, run the following command:

 ```bash
 poetry add connectiva
 ```

 ### Using pip

 Alternatively, you can install Connectiva using pip:

 ```bash
 pip install connectiva
 ```

 ## Supported Protocols

 Connectiva supports the following communication protocols:

 - [ ] **REST APIs**
 - [ ] **gRPC**
 - [X] **Kafka**
 - [X] **RabbitMQ (and other message brokers)**
 - [X] **WebSockets**
 - [ ] **GraphQL**
 - [X] **File-based communication**

 ## Usage

 Here's a quick guide to using Connectiva in your Python projects:

 ### 1. Initialize Connectiva

 ```python
 from connectiva import Connectiva, Message

 # Instantiate Connectiva with desired configuration
 connectiva = Connectiva(
     endpoint="kafka://localhost:9092",
     broker_list="localhost:9092",
     topic="my_topic",
     group_id="my_group"
 )
 ```

 ### 2. Connect to the Communication Endpoint

 ```python
 connectiva.connect()
 ```

 ### 3. Send a Message

 ```python
 message = Message(action="process", data="Hello, Kafka!")
 response = connectiva.send(message)
 print(f"Response: {response}")
 ```

 ### 4. Receive a Message

 ```python
 received_message = connectiva.receive()
 print(f"Received: {received_message}")
 ```

 ### 5. Disconnect

 ```python
 connectiva.disconnect()
 ```

 ## Configuration

 Connectiva is designed to be flexible and can be configured to suit your needs. Here's an example configuration:

 ```python
 connectiva = Connectiva(
     endpoint="grpc://localhost:50051",
     topic="my_topic",
     queue_name="my_queue",
 )
 ```

 ## Extending Connectiva

 Connectiva is built with extensibility in mind. You can easily extend the library by adding new communication strategies or customizing existing ones. Simply create a new strategy class that implements the `CommunicationMethod` interface and add it to the strategy map.

 ## Contributing

 We welcome contributions to Connectiva! If you'd like to contribute, please follow these steps:

 1. Fork the repository.
 2. Create a new branch for your feature or bugfix.
 3. Make your changes and commit them.
 4. Push your changes to your fork.
 5. Create a pull request on the main repository.

 Please ensure that your code follows the project's style guidelines and includes appropriate tests.

 ## License

 Connectiva is released under the MIT License. See the [LICENSE](LICENSE) file for more details.

 ## Authors

 - **Ali Tavallaie** - [a.tavallaie@gmail.com](mailto:a.tavallaie@gmail.com)

 ---

 Thank you for using Connectiva! We hope it simplifies your microservice communication needs.
