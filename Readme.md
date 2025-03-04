## API Endpoints Documentation

### Overview

This document provides detailed information about the API endpoints available in the Django application. These endpoints allow users to sign up, log in, create, delete, and fetch alerts. Authentication is handled using JWT (JSON Web Tokens), and some endpoints require the user to be authenticated.

### Authentication Endpoints

#### 1. Sign Up

- **URL:** `/signup/`
- **Method:** `POST`
- **Description:** Creates a new user account.
- **Request Body:**
  - `username` (string): Desired username.
  - `password` (string): Desired password.
- **Responses:**
  - **201 Created:** User created successfully.
  - **400 Bad Request:** Username already exists.

#### 2. Log In

- **URL:** `/login/`
- **Method:** `POST`
- **Description:** Authenticates a user and returns JWT access and refresh tokens.
- **Request Body:**
  - `username` (string): Username.
  - `password` (string): Password.
- **Responses:**
  - **200 OK:** Returns access and refresh tokens.
  - **400 Bad Request:** Invalid credentials.

### Alert Management Endpoints

#### 3. Create Alert

- **URL:** `/create_alert/`
- **Method:** `POST`
- **Description:** Creates a new alert for the authenticated user.
- **Request Headers:** `Authorization: Bearer <jwt_access_token>`
- **Request Body:**
  - `target_price` (string): Target price for the alert.
  - `trigger_condition` (string): Condition for triggering the alert (e.g., "below").
  - `email` (string): Email address to notify.
- **Responses:**
  - **201 Created:** Alert created successfully.
  - **400 Bad Request:** Missing required fields or invalid target price.

#### 4. Delete Alert

- **URL:** `/delete_alert/`
- **Method:** `POST`
- **Description:** Marks an alert as deleted.
- **Request Headers:** `Authorization: Bearer <jwt_access_token>`
- **Request Body:**
  - `alert_id` (integer): ID of the alert to delete.
- **Responses:**
  - **200 OK:** Alert marked as deleted.
  - **400 Bad Request:** Missing alert ID, alert already deleted, or alert does not exist.

#### 5. Fetch Alerts

- **URL:** `/fetch_alerts/`
- **Method:** `GET`
- **Description:** Fetches all alerts for the authenticated user, optionally filtered by state.
- **Request Headers:** `Authorization: Bearer <jwt_access_token>`
- **Request Parameters (optional):**
  - `state` (string): Filter alerts by state (`created`, `triggered`, or `deleted`).
- **Responses:**
  - **200 OK:** Returns a list of alerts.
  - **400 Bad Request:** Invalid state parameter.

### Permissions

- **Authenticated Endpoints:** Creating, deleting, and fetching alerts require the user to be authenticated using JWT tokens.
- **Public Endpoints:** The sign-up and log-in endpoints do not require authentication.

### Models

#### Alert Model

- **Fields:**
  - `user`: ForeignKey to the `User` model.
  - `target_price`: The target price for the alert.
  - `trigger_condition`: Condition for triggering the alert (e.g., "below").
  - `email`: Email address to notify.
  - `state`: State of the alert (e.g., "created", "triggered", "deleted").

### Example Usage

#### Sign Up

To sign up a new user, send a POST request to `/api/signup/` with the desired username and password.

#### Log In

To log in, send a POST request to `/api/login/` with the username and password. If successful, you will receive JWT access and refresh tokens.

#### Create Alert

To create an alert, send a POST request to `/api/alerts/create/` with the target price, trigger condition, and email. Make sure to include the JWT access token in the Authorization header.

#### Delete Alert

To delete an alert, send a POST request to `/api/alerts/delete/` with the alert ID. Include the JWT access token in the Authorization header.

#### Fetch Alerts

To fetch alerts, send a GET request to `/api/alerts/`. Optionally, you can include a state parameter to filter alerts by their state. Include the JWT access token in the Authorization header.

### Common Errors

- **400 Bad Request:** Generally indicates missing or invalid input data.
- **401 Unauthorized:** Indicates that the request requires authentication.
- **404 Not Found:** Typically indicates that a resource (such as an alert) does not exist.
## WebSocket Price Monitor and Alert System


## WebSocket Price Monitoring

This application monitors cryptocurrency prices in real-time via a WebSocket connection and triggers alerts based on predefined conditions stored in a PostgreSQL database. Alerts are pushed to RabbitMQ for further processing, such as sending email notifications.

### Overview

The system consists of the following components:
- **WebSocket Client**: Connects to Binance WebSocket to receive real-time price updates.
- **PostgreSQL Database**: Stores user-defined alerts.
- **RabbitMQ**: Message broker to handle triggered alerts.

### Components

#### Environment Variables

Ensure the following environment variables are set:

- `RABBITMQ_HOST`: Hostname for the RabbitMQ server.
- `RABBITMQ_QUEUE`: Name of the RabbitMQ queue.
- `DATABASE_SETTINGS__DBNAME`: Name of the PostgreSQL database.
- `DATABASE_SETTINGS__USER`: PostgreSQL username.
- `DATABASE_SETTINGS__PASSWORD`: PostgreSQL password.
- `DATABASE_SETTINGS__HOST`: Hostname for the PostgreSQL server.
- `DATABASE_SETTINGS__PORT`: Port number for the PostgreSQL server.

#### RabbitMQ Setup

The RabbitMQ setup involves connecting to the RabbitMQ server and publishing messages to a specified queue. The connection parameters are provided through environment variables, and the queue is declared as durable to ensure message persistence.

#### PostgreSQL Setup

##### Fetching Alerts

The function connects to the PostgreSQL database using the provided credentials and fetches alerts that are in the "created" state. This is done using a named cursor to allow for streaming results, which is more efficient for large datasets.

##### Updating Alert State

This function updates the state of an alert in the PostgreSQL database. It connects to the database and executes an update query to change the alert's state to "triggered".

#### Handling Price Updates

This function processes incoming price updates and checks each alert to see if the condition is met (e.g., price is above or below the target price). If the condition is met, an alert message is prepared and pushed to RabbitMQ. The state of the alert is then updated to "triggered" in the database.

#### WebSocket Client

##### WebSocket Handlers

- **on_message**: Parses incoming WebSocket messages to extract the current price and triggers the price update handling function.
- **on_error**: Logs any errors encountered during the WebSocket connection.
- **on_close**: Logs the closure of the WebSocket connection.
- **on_open**: Logs the opening of the WebSocket connection.

##### Running the WebSocket Client

The WebSocket client connects to the Binance WebSocket stream for real-time price updates. It handles incoming messages, errors, and connection events, ensuring continuous monitoring of the specified cryptocurrency prices.

## Email Notification Service

This script listens for messages from RabbitMQ and sends email notifications based on the received alerts. It uses the `smtplib` library for sending emails and the `pika` library to interface with RabbitMQ.

### Overview

The Email Notification Service performs the following tasks:
- **Connects to RabbitMQ**: Listens for messages on a specified queue.
- **Processes Messages**: Parses the alert messages received from RabbitMQ.
- **Sends Emails**: Sends email notifications using SMTP based on the parsed alert data.

### Components

#### Environment Variables

Ensure the following environment variables are set for RabbitMQ:

- `RABBITMQ_HOST`: Hostname for the RabbitMQ server.
- `RABBITMQ_QUEUE`: Name of the RabbitMQ queue.

#### Email Configuration

The script uses the following SMTP server configuration:

- `smtp_server`: The SMTP server address (e.g., 'smtp.google.com').
- `smtp_port`: The SMTP server port (usually 587 for TLS).
- `smtp_user`: The SMTP username.
- `smtp_password`: The SMTP password.
- `from_email`: The email address from which alerts are sent.

#### Functions

##### `send_email`

This function sends an email using the specified SMTP server settings.

- **Parameters:**
  - `subject`: Subject of the email.
  - `body`: Body content of the email.
  - `to_email`: Recipient's email address.
  - `from_email`: Sender's email address.
  - `smtp_server`: SMTP server address.
  - `smtp_port`: SMTP server port.
  - `smtp_user`: SMTP username.
  - `smtp_password`: SMTP password.

- **Functionality:** 
  - Creates a multipart email message.
  - Connects to the SMTP server.
  - Sends the email and handles any exceptions that occur during this process.

##### `callback`

This function is called when a message is received from RabbitMQ.

- **Parameters:**
  - `ch`: The channel object.
  - `method`: The method frame from RabbitMQ.
  - `properties`: Message properties.
  - `body`: The message body in JSON format.

- **Functionality:**
  - Parses the alert message to extract details such as the target price and recipient email.
  - Calls `send_email` to send the alert notification.

##### `main`

The main function sets up and runs the RabbitMQ consumer.

- **Functionality:**
  - Connects to RabbitMQ using the provided host.
  - Declares the queue to ensure it exists.
  - Sets up a subscription to the queue and specifies the `callback` function to handle messages.
  - Starts consuming messages from the queue.

### Example Usage

1. **Configure Environment Variables**: Set `RABBITMQ_HOST` and `RABBITMQ_QUEUE` in your environment.
2. **SMTP Configuration**: Ensure the SMTP server settings (`smtp_server`, `smtp_port`, `smtp_user`, `smtp_password`, and `from_email`) are correctly configured in the script.
3. **Run the Script**: Execute the script to start listening for messages from RabbitMQ and send email notifications.

## Seperating each service with Docker
The system is divided into several services, each running in its own Docker container. Docker Compose is used to define and manage these services, ensuring they work together seamlessly.

### Services

#### Web Service (Django Application)

- **Purpose**: Hosts the Django web application, which includes APIs for user management and alert creation.
- **Configuration**:
  - **Image**: Built from the `./api_endpoints` directory.
  - **Ports**: Exposes port `8000` for accessing the Django application.
  - **Environment Variables**: Configures Django settings and database connections.
  - **Dependencies**: Waits for the PostgreSQL database to be available before starting.

#### PostgreSQL Service

- **Purpose**: Provides a relational database to store user data and alerts.
- **Configuration**:
  - **Image**: Uses the official `postgres:latest` image.
  - **Ports**: Maps port `5432` for database connections.
  - **Environment Variables**: Sets database name, user, and password.
  - **Volumes**: Persists data using a named volume (`postgres_data`), ensuring data durability.

#### Price Monitor Service

- **Purpose**: Monitors cryptocurrency prices in real-time and sends alerts based on predefined conditions.
- **Configuration**:
  - **Image**: Built from the `./price_monitor` directory.
  - **Command**: Runs the `monitor.py` script.
  - **Environment Variables**: Configures connections to RabbitMQ and PostgreSQL.
  - **Dependencies**: Waits for RabbitMQ and PostgreSQL services to be available.

#### RabbitMQ Service

- **Purpose**: Acts as a message broker, handling alerts from the price monitor and distributing them to the email service.
- **Configuration**:
  - **Image**: Uses the official `rabbitmq:latest` image.
  - **Ports**: Exposes ports `5672` for messaging and `15672` for the management plugin.
  - **Environment Variables**: Sets default user credentials.
  - **Volumes**: Persists data using a named volume (`rabbitmq_data`).

#### Email Service

- **Purpose**: Sends email notifications based on alerts received from RabbitMQ.
- **Configuration**:
  - **Image**: Built from the `./send_alert` directory.
  - **Command**: Runs the `consumer.py` script.
  - **Environment Variables**: Configures connection details for RabbitMQ.
  - **Dependencies**: Waits for RabbitMQ to be available.

### Volumes

- **`postgres_data`**: Ensures that PostgreSQL data is not lost when containers are stopped or removed.
- **`rabbitmq_data`**: Ensures that RabbitMQ data, including messages and broker state, is preserved.

### Workflow

1. **Startup**: Docker Compose starts all services, ensuring that dependencies are properly managed.
2. **Price Monitoring**: The price monitor service connects to a WebSocket for real-time price updates, processes the data, and sends alerts to RabbitMQ.
3. **Alert Handling**: RabbitMQ queues the alerts, which are then consumed by the email service.
4. **Email Notification**: The email service sends out notifications to users based on the alerts.

### Benefits

- **Isolation**: Each service runs in its own container, isolating dependencies and configurations.
- **Scalability**: Services can be scaled independently based on load.
- **Portability**: The Docker setup ensures consistent environments across different stages of development and production.

By containerizing the entire system, Docker simplifies deployment and management, ensuring that each component interacts smoothly within a controlled environment.
