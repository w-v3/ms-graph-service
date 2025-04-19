from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.dependencies import get_email_manager
from app.schemas.email import EmailCreate
from app.schemas.responses import FetchEmailsResponse, SendEmailResponse
from app.services.email_manager import EmailManager

router = APIRouter()

@router.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify that the application is running.
    """
    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "All good"})

@router.post(
    "/send",
    tags=["Business Logic"],
    response_model=SendEmailResponse,
    status_code=status.HTTP_200_OK,
    summary="Send an email and echo the request",
)
async def send_email(
    email: EmailCreate,
    manager: EmailManager = Depends(get_email_manager),
) -> SendEmailResponse:
    graph_status: int = await manager.send_email(email)
    if not graph_status:
        return SendEmailResponse(status_code=500, email=email , message="error inn sending mail")
    return SendEmailResponse(status_code=200, email=email , message="Email Sent")


@router.get(
    "/fetch",
    tags=["Business Logic"],
    response_model=FetchEmailsResponse,
    status_code=status.HTTP_200_OK,
    summary="Fetch new emails and report count",
)
@router.get("/fetch")
async def fetch_emails(
    manager: EmailManager = Depends(get_email_manager),
):
    messages = await manager.sync_and_store_emails()
    return FetchEmailsResponse(status_code=200, count=len(messages))
