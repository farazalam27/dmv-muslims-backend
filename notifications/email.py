import logging
import httpx
from typing import Dict, Any, List, Optional
from config import settings

logger = logging.getLogger(__name__)

# Email templates
TEMPLATES = {
    "submission_approved": {
        "subject": "Your submission has been approved",
        "html": """
        <h1>Your submission has been approved!</h1>
        <p>Thank you for contributing to the DMV Muslims platform.</p>
        <p>Your submission is now live on the platform.</p>
        """
    },
    "submission_rejected": {
        "subject": "Your submission needs revision",
        "html": """
        <h1>Your submission needs revision</h1>
        <p>Thank you for contributing to the DMV Muslims platform.</p>
        <p>Unfortunately, we couldn't approve your submission for the following reason:</p>
        <p><strong>{reason}</strong></p>
        <p>Please feel free to revise and resubmit.</p>
        """
    },
    "submission_review": {
        "subject": "New submission pending review",
        "html": """
        <h1>New submission pending review</h1>
        <p>A new {entity_type} has been submitted by {submitted_by}.</p>
        <p>Please review it at: <a href="{review_url}">{review_url}</a></p>
        """
    },
    "claim_received": {
        "subject": "Business claim: {business_name}",
        "html": """
        <h1>New business claim</h1>
        <p>A user has claimed ownership of: <strong>{business_name}</strong></p>
        <p>Please review the claim.</p>
        """
    }
}

async def send_email(
    to: str,
    subject: str,
    template: str,
    data: Optional[Dict[str, Any]] = None,
    from_email: str = "noreply@dmvmuslims.com",
    from_name: str = "DMV Muslims",
) -> bool:
    """
    Send an email using Resend API
    
    Args:
        to: Recipient email address
        subject: Email subject
        template: Template name from TEMPLATES
        data: Data to format the template with
        from_email: Sender email address
        from_name: Sender name
        
    Returns:
        True if email was sent successfully, False otherwise
    """
    if not settings.RESEND_API_KEY:
        logger.warning("RESEND_API_KEY not set, email not sent")
        return False
        
    if template not in TEMPLATES:
        logger.error(f"Email template not found: {template}")
        return False
        
    try:
        # Get template
        template_data = TEMPLATES[template]
        
        # Format subject and HTML with data
        formatted_subject = template_data["subject"].format(**(data or {}))
        formatted_html = template_data["html"].format(**(data or {}))
        
        # Prepare payload for Resend API
        payload = {
            "from": f"{from_name} <{from_email}>",
            "to": to,
            "subject": formatted_subject,
            "html": formatted_html,
        }
        
        # In a real implementation, we would send the email using Resend API
        # For now, just log that we would send it
        logger.info(f"Would send email to {to}: {formatted_subject}")
        
        # This would be the actual API call
        # async with httpx.AsyncClient() as client:
        #     response = await client.post(
        #         "https://api.resend.com/emails",
        #         json=payload,
        #         headers={"Authorization": f"Bearer {settings.RESEND_API_KEY}"}
        #     )
        #     if response.status_code == 200:
        #         logger.info(f"Email sent to {to}")
        #         return True
        #     else:
        #         logger.error(f"Failed to send email: {response.text}")
        #         return False
        
        return True
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return False

class AdminNotifier:
    """Helper class for sending notifications to admins"""
    
    async def notify_new_submission(self, submission: Dict[str, Any]) -> bool:
        """Alert admins of pending submissions"""
        # In a real implementation, we would get admin emails from the database
        admin_emails = ["admin@dmvmuslims.com"]
        
        for email in admin_emails:
            await send_email(
                to=email,
                subject="New Submission Pending Review",
                template="submission_review",
                data={
                    "entity_type": submission.get("entity_type", "item"),
                    "submitted_by": submission.get("submitted_by", "a user"),
                    "review_url": f"https://admin.dmvmuslims.com/submissions/{submission.get('id')}"
                }
            )
        
        return True
    
    async def notify_claim_received(self, claim_id: str, business_name: str) -> bool:
        """Alert admins of new business claims"""
        # In a real implementation, we would get admin emails from the database
        admin_emails = ["admin@dmvmuslims.com"]
        
        for email in admin_emails:
            await send_email(
                to=email,
                subject=f"Business Claim: {business_name}",
                template="claim_received",
                data={"claim_id": claim_id, "business_name": business_name}
            )
        
        return True
    
    async def notify_submission_result(self, user_email: str, status: str, reason: str = None) -> bool:
        """Notify user of submission approval/rejection"""
        template = "submission_approved" if status == "approved" else "submission_rejected"
        
        return await send_email(
            to=user_email,
            subject=f"Submission {status.capitalize()}",
            template=template,
            data={"reason": reason or "No specific reason provided."}
        )