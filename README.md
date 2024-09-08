# Event Recommender App

## Team Members:
- [Sean Clewis]
- This Repo Only Contains the server side info which I have handled and I left my partners work off who focused on the front end for the sake of privacy

## Purpose:

The purpose of this project is develop the backend for a mobile application. The app will get the users' preferences, location, and other information. and find events near the user with matching criteria. This project uses PredictHQ for their api to get events. 

(NOTE: Predict hq requires a subscription to their platform in order to use their api. My subscription is currently inactive. In order for this program to work, create your own account with predict HQ and replace the API key with yours. )

## High Level Design:
Server Side:

    The server side handles incoming requests from clients, processes them, and sends back responses.
    It consists of a network layer responsible for handling incoming connections and routing requests to appropriate handlers.
    The network layer deserializes incoming JSON data and passes it to the server application layer.
    The server application layer interprets the requests, performs necessary actions, and prepares responses.
    After processing, the server application layer serializes the response data into JSON format and sends it back to the client.
    The network layer then sends the JSON response to the appropriate client.

Communication Protocol:

    The communication between client and server follows a request-response pattern.
    Clients initiate requests by sending JSON-formatted messages containing commands or data to the server.
    Servers respond to client requests with JSON-formatted messages containing the results of the requested actions or any relevant data.
    Both clients and servers should agree upon a set of predefined JSON message formats for requests and responses to ensure interoperability.

### Server implementation:
To run the server, first run python3 create_database.py to set up the database. you will get a users.db file in your directory

Next run the server, python3 server.py

The server accepts request from the client and will perform the appropriate actions based on the data recieved

A test client file has been created to simulate sending data to server

All python3 client.py or python3 client.py -h to bring up the help menu that displays all flags and commands available

All the commands in the help menu are fully functional. The help menu will show you the flags available, how to run the commands, and the flags required per command. 

The server accepts the commands sent to the client via JSON data. After reciving a command the server will display the address from the client that requested the command as well as the command and the JSON data sent. The server will then send JSON data back to the client. The content varies per command, However, the general format is a status which indicates if the request succeeded or failed and a message from the server. 

The server sets up a socket using local host on port 9000. IT then proceeds to bind, listen, then accept any requests from clients. 

There is also a demo video of the project that you can view that shows how it functions.


