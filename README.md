# Microsoft Graph Email Service

This is a FastAPI-based service that integrates with the Microsoft Graph API to send and receive emails. It supports token caching and provides both REST API endpoints and background processing using APScheduler.

## Prerequisites

- Python 3.11+
- MongoDB instance (local or remote)
- MIcrosoft Outlook Account and a valid inbox
- Microsoft Azure application with proper API permissions for Mail.ReadWrite, Mail.Send , User.Read
- If running with Docker: Docker and Docker Compose installed

## Environment Configuration

Configuration is handled via a `.env` file. This includes Microsoft Graph API credentials and MongoDB URI. A sample set of required environment variables is below:

```
CLIENT_ID=your-microsoft-app-client-id
TENANT_ID=your-microsoft-tenant-id
MS_GRAPH_API_URL=https://graph.microsoft.com/v1.0/me
MS_GRAPH_AUTH_URL=https://login.microsoftonline.com
SCOPES=Mail.ReadWrite,Mail.Send  # comma-separated
MONGO_AUTH_USERNAME=your-mongo-username
MONGO_AUTH_PASSWORD=password123
MONGO_SERVER_ADDRESS=ip-address-for-mongo-server
MONGO_SERVER_PORT=27017
MONGO_DB_NAME=emaildb
USER_EMAIL=your-email@example.com
PROJECT_NAME=Microsoft Graph API Email Service
API_V1_STR=/api/v1
EMAIL_RETRIEVAL_INTERVAL_MINUTES=2
```

**Note:** The `SCOPES` field must use comma-separated values, and `offline_access` is not required for this flow.

If using Docker, the Dockerfile and docker-compose.yml are included. Ensure Docker is installed on your system.



## How to Run the App

### Locally

1. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the app:
   ```bash
   uvicorn app.main:app --reload
   ```

### Using Docker

To build and run the app with Docker:

```bash
docker-compose up --build
```

## Running Tests

1. Install dev requirements:
   ```bash
   pip install -r requirements-dev.txt
   ```

2. Run tests with pytest:
   ```bash
   pytest --disable-warnings --maxfail=1 -v
   ```

## Functionality

- **/health**: Check service status
- **/send**: Send email using Microsoft Graph API
- **/fetch**: Fetch new emails and store them in MongoDB
- **Token Caching**: Device code flow caches token in `token_cache.json`
- **MongoDB**: Emails are stored and queried from MongoDB

## Notes / Additional Information

- **Token Cache**: `token_cache.json` stores the OAuth tokens using MSAL’s serializable cache. This is necessary for reusing tokens in cron job style setups.
- **Device Code Flow Limitations**: Personal Microsoft accounts require interactive login when tokens expire. This limits automation with background jobs.
- **Recommended Setup**: For full automation without interactive logins, use a work/school account with admin access to grant proper permissions.

## Additional Files

- `.dockerignore` and `.gitignore`: Specify ignored files/folders for Docker and Git.
- `.vscode/settings.json`: Recommended VSCode settings.
- `pyproject.toml`: Configuration for formatting, linting, and static type checking using ruff and mypy.
- `scripts/`: Contains shell scripts for formatting, linting, and testing (e.g., `format.sh`, `lint.sh`, `typecheck.sh`, `test.sh`).

## Security

- All sensitive credentials are stored in environment variables
- Microsoft Graph API authentication using MSAL
- Secure MongoDB connection

## How I Used AI Coding Tools

This project was developed with the assistance of AI coding tools for:
- Code structure and organization
- Documentation generation
- Test case suggestions

## License

MIT 