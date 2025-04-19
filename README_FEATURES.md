# Microsoft Graph Email Service

This service provides an end-to-end integration between a personal Microsoft Outlook account and MongoDB using the Microsoft Graph API. It supports sending and fetching emails, storing them in a database, and running scheduled background tasks.

## Implemnted Features

- **Authentication using MSAL**: Authenticate personal Microsoft accounts using the `msal` library and OAuth 2.0 Device Code Flow.
- **Token Caching**: Utilizes `SerializableTokenCache` to cache tokens locally, allowing non-interactive token reuse.
- **Send Emails**: Send HTML-formatted emails via Microsoft Graph API using an authenticated personal Outlook account.
- **Fetch Emails**: Periodically fetch emails using the `/messages` endpoint and filter by the latest received datetime.
- **MongoDB Integration**: Store emails in a MongoDB database, supporting upsert and fetch operations.
- **Design Patterns**: Structured modular code using patterns such as dependency injection, interface abstraction, and separation of concerns.
- **Over 90% Test Coverage**: Comprehensive test suite using `pytest`, mocking, and FastAPI test client for both unit and API endpoint testing.
- **Background Scheduling**: Uses APScheduler to periodically trigger background jobs for syncing emails.
- **FastAPI-based API**: Exposes RESTful endpoints for sending and fetching emails.
- **Dockerized Setup**: Includes Dockerfile and docker-compose for easy deployment and environment isolation.
- **Environment-based Config**: Uses a `.env` file to manage secrets and environment-specific settings.
- **Development Tooling**: Includes configuration for `mypy`, `ruff`, and `black` for static type checks, linting, and formatting.
- **Scripts Directory**: Contains scripts for formatting, linting, testing, and managing the app lifecycle.
- **Flexible Email Schema**: Stores metadata and attachments along with emails for future enhancements.
- **Device Code Flow Constraints Handling**: Notes and logic to manage re-authentication needs due to personal Microsoft account limitations.
- Error Handling and Logging
- Add Swagger/OpenAPI documentation UI for easy exploration of email APIs.


## Future Improvements

The following enhancements and improvements are envisioned for the Microsoft Graph Email Service project:

## 1. Enhanced Token Caching Mechanism
- Implement a more robust and scalable caching mechanism for storing authentication tokens, such as Redis or in-memory cache services instead of a local file.

## 2. Email Sending Enhancements
- Add support for sending emails with attachments.
- Extend functionality to handle various body formats (HTML, plain text).
- Enable sending emails with BCC (Blind Carbon Copy) and CC (Carbon Copy) recipients.
- Support for maintaining and handling email threads, possibly by updating MongoDB schema to accommodate conversation/thread IDs.

## 3. Email Fetching Improvements
- Introduce pagination when fetching emails to handle large volumes efficiently and avoid payload overflows.
- Better filtering and sorting mechanisms to retrieve emails based on more advanced criteria.

## 4. Asynchronous Task Handling
- Replace APScheduler with a more powerful asynchronous task queue like Celery combined with RabbitMQ or Redis.
- Helps in better managing time-consuming operations such as:
  - Sending bulk emails with attachments.
  - Pre-processing email contents using AI or ML modules.
  - Data ingestion and transformation for analytics.

## 5. Cloud Integration for Attachments
- Integrate with cloud providers (Azure Blob Storage, AWS S3, etc.) for uploading and accessing attachments independently of the email storage.

## 6. Non-Interactive Authentication Flow
- Support for completely non-interactive OAuth2 flows by using a Microsoft Work or Organizational account with admin access.
- This enables setting up proper API permissions and seamless access token generation and renewal.

## 7. Logging, Monitoring, and Alerting
- Improve observability by integrating structured logging (e.g., with Loguru), tracing, and metrics collection (e.g., with Prometheus/Grafana).
- Add health checks and alerting for email sending/fetching failures.

## 8. Enhanced Developer Experience
- Improve environment bootstrapping using Makefiles or shell scripts.

## 9. Modular Feature Extensibility
- Create pluggable modules for third-party services (e.g., Gmail API, Zoho, etc.) for a more generic and extendable email orchestration platform.

---
