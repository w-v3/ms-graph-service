from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field


class EmailBase(BaseModel):
    recipients: list[str]
    subject: str
    body: str
    attachments: list[str] | None = None


class EmailCreate(EmailBase):
    pass


class EmailAddress(BaseModel):
    name: str | None
    address: EmailStr | None

    class Config:
        populate_by_name = True


class Recipient(BaseModel):
    email_address: EmailAddress = Field(..., alias="emailAddress")

    class Config:
        populate_by_name = True


class Body(BaseModel):
    content_type: str = Field(..., alias="contentType")
    content: str

    class Config:
        populate_by_name = True


class EmailInDB(BaseModel):
    odata_etag: str | None = Field(None, alias="@odata.etag")
    id: str = Field(..., alias="_id")
    created_date_time: datetime = Field(..., alias="createdDateTime")
    last_modified_date_time: datetime = Field(..., alias="lastModifiedDateTime")
    change_key: str = Field(..., alias="changeKey")
    categories: list[str]
    received_date_time: datetime = Field(..., alias="receivedDateTime")
    sent_date_time: datetime = Field(..., alias="sentDateTime")
    has_attachments: bool = Field(..., alias="hasAttachments")
    internet_message_id: str | None = Field(None, alias="internetMessageId")
    subject: str | None
    body_preview: str | None = Field(None, alias="bodyPreview")
    importance: str | None
    parent_folder_id: str | None = Field(None, alias="parentFolderId")
    conversation_id: str | None = Field(None, alias="conversationId")
    conversation_index: str | None = Field(None, alias="conversationIndex")
    is_delivery_receipt_requested: bool | None = Field(
        None,
        alias="isDeliveryReceiptRequested",
    )
    is_read_receipt_requested: bool | None = Field(None, alias="isReadReceiptRequested")
    is_read: bool | None = Field(None, alias="isRead")
    is_draft: bool | None = Field(None, alias="isDraft")
    web_link: str | None = Field(None, alias="webLink")
    inference_classification: str | None = Field(None, alias="inferenceClassification")
    body: Body | None
    sender: Recipient | None
    from_: Recipient | None = Field(None, alias="from")
    to_recipients: list[Recipient] | None = Field(None, alias="toRecipients")
    cc_recipients: list[Recipient] | None = Field(None, alias="ccRecipients")
    bcc_recipients: list[Recipient] | None = Field(None, alias="bccRecipients")
    reply_to: list[Recipient] | None = Field(None, alias="replyTo")
    flag: dict[str, Any] | None

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
