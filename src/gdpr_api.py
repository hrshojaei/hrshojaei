"""
GDPR/DSGVO API endpoints for candidate data management
Implements data subject rights: access, rectification, erasure, portability, restriction
"""

from fastapi import APIRouter, HTTPException, Query, Body, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict
from datetime import datetime
import json

from src.candidate_manager import CandidateManager
from src.consent_token import ConsentTokenManager
from src.config import settings
from loguru import logger

router = APIRouter(prefix="/gdpr", tags=["GDPR/DSGVO"])

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="src/templates")


# ========== Request/Response Models ==========

class ConsentRequest(BaseModel):
    """Request model for giving consent"""
    candidate_id: int
    consent_method: str = "web"  # phone, email, web, sms
    consent_version: str = "v1.0"
    recording_consent: bool = False
    marketing_consent: bool = False
    retention_days: int = 730  # 2 years


class ConsentResponse(BaseModel):
    """Response model for consent operations"""
    success: bool
    message: str
    candidate_id: int
    consent_given: bool
    consent_timestamp: Optional[str] = None


class DataExportResponse(BaseModel):
    """Response model for data export"""
    success: bool
    message: str
    export_data: Optional[Dict] = None
    export_timestamp: str


class DeletionRequest(BaseModel):
    """Request model for data deletion"""
    candidate_id: Optional[int] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    anonymize: bool = False  # If True, anonymize instead of full deletion


class DeletionResponse(BaseModel):
    """Response model for data deletion"""
    success: bool
    message: str
    deletion_type: str  # "full_deletion" or "anonymization"
    deletion_timestamp: str


# ========== API Endpoints ==========

@router.post("/consent/give", response_model=ConsentResponse)
async def give_consent(request: ConsentRequest):
    """
    Give consent for data processing (GDPR Art. 6)

    **Use case:** Candidate explicitly gives consent for data processing

    **Example:**
    ```json
    {
        "candidate_id": 123,
        "consent_method": "web",
        "recording_consent": true,
        "marketing_consent": false
    }
    ```
    """
    try:
        manager = CandidateManager()

        # Check if candidate exists
        candidate = manager.get_candidate(candidate_id=request.candidate_id)
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")

        # Set consent
        success = manager.set_consent(
            candidate_id=request.candidate_id,
            consent_given=True,
            consent_method=request.consent_method,
            consent_version=request.consent_version,
            recording_consent=request.recording_consent,
            marketing_consent=request.marketing_consent,
            retention_days=request.retention_days
        )

        if success:
            # Get updated candidate
            candidate = manager.get_candidate(candidate_id=request.candidate_id)

            return ConsentResponse(
                success=True,
                message="Consent successfully recorded",
                candidate_id=request.candidate_id,
                consent_given=True,
                consent_timestamp=candidate.consent_timestamp if candidate else None
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to record consent")

    except Exception as e:
        logger.error(f"Error giving consent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/consent/revoke", response_model=ConsentResponse)
async def revoke_consent(
    candidate_id: Optional[int] = Body(None),
    phone: Optional[str] = Body(None),
    email: Optional[str] = Body(None)
):
    """
    Revoke consent and opt-out (GDPR Art. 7(3))

    **Use case:** Candidate wants to withdraw consent

    **Parameters:**
    - candidate_id OR phone OR email (at least one required)

    **Example:**
    ```json
    {
        "phone": "+4915112345678"
    }
    ```
    """
    try:
        manager = CandidateManager()

        # Find candidate
        candidate = None
        if candidate_id:
            candidate = manager.get_candidate(candidate_id=candidate_id)
        elif phone:
            candidate = manager.get_candidate(phone=phone)
        elif email:
            # Search by email (would need to add method to CandidateManager)
            raise HTTPException(
                status_code=501,
                detail="Email search not yet implemented. Please use phone or candidate_id"
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Please provide candidate_id, phone, or email"
            )

        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")

        # Revoke consent
        success = manager.revoke_consent(candidate.id)

        if success:
            return ConsentResponse(
                success=True,
                message="Consent successfully revoked. You will not be contacted again.",
                candidate_id=candidate.id,
                consent_given=False,
                consent_timestamp=None
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to revoke consent")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error revoking consent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data/export", response_model=DataExportResponse)
async def export_candidate_data(
    candidate_id: Optional[int] = Query(None),
    phone: Optional[str] = Query(None)
):
    """
    Export all candidate data (GDPR Art. 20 - Right to data portability)

    **Use case:** Candidate requests all their stored data

    **Parameters:**
    - candidate_id OR phone (at least one required)

    **Example:**
    ```
    GET /gdpr/data/export?phone=%2B4915112345678
    ```

    **Returns:** JSON with all candidate data including call logs and transcripts
    """
    try:
        manager = CandidateManager()

        # Find candidate
        candidate = None
        if candidate_id:
            candidate = manager.get_candidate(candidate_id=candidate_id)
        elif phone:
            candidate = manager.get_candidate(phone=phone)
        else:
            raise HTTPException(
                status_code=400,
                detail="Please provide candidate_id or phone"
            )

        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")

        # Export data
        export_data = manager.export_candidate_data(candidate.id)

        if export_data:
            return DataExportResponse(
                success=True,
                message="Data export successful",
                export_data=export_data,
                export_timestamp=datetime.now().isoformat()
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to export data")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/data/delete", response_model=DeletionResponse)
async def delete_candidate_data(request: DeletionRequest):
    """
    Delete or anonymize candidate data (GDPR Art. 17 - Right to erasure)

    **Use case:** Candidate requests deletion of their data

    **Parameters:**
    - candidate_id OR phone OR email (at least one required)
    - anonymize: If true, anonymizes data instead of full deletion

    **Example:**
    ```json
    {
        "phone": "+4915112345678",
        "anonymize": false
    }
    ```

    **Note:** Full deletion removes all data. Anonymization keeps anonymized
    records for statistical purposes.
    """
    try:
        manager = CandidateManager()

        # Find candidate
        candidate = None
        if request.candidate_id:
            candidate = manager.get_candidate(candidate_id=request.candidate_id)
        elif request.phone:
            candidate = manager.get_candidate(phone=request.phone)
        elif request.email:
            raise HTTPException(
                status_code=501,
                detail="Email search not yet implemented. Please use phone or candidate_id"
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Please provide candidate_id, phone, or email"
            )

        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")

        # Delete or anonymize
        success = manager.delete_candidate_data(
            candidate_id=candidate.id,
            anonymize=request.anonymize
        )

        if success:
            deletion_type = "anonymization" if request.anonymize else "full_deletion"
            message = (
                "Data successfully anonymized" if request.anonymize
                else "All data successfully deleted"
            )

            return DeletionResponse(
                success=True,
                message=message,
                deletion_type=deletion_type,
                deletion_timestamp=datetime.now().isoformat()
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to delete/anonymize data")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/consent/check")
async def check_consent(
    candidate_id: Optional[int] = Query(None),
    phone: Optional[str] = Query(None)
):
    """
    Check if candidate has valid consent (GDPR compliance check)

    **Use case:** Verify consent before contacting candidate

    **Parameters:**
    - candidate_id OR phone (at least one required)

    **Example:**
    ```
    GET /gdpr/consent/check?phone=%2B4915112345678
    ```

    **Returns:** Consent status and details
    """
    try:
        manager = CandidateManager()

        # Find candidate
        candidate = None
        if candidate_id:
            candidate = manager.get_candidate(candidate_id=candidate_id)
        elif phone:
            candidate = manager.get_candidate(phone=phone)
        else:
            raise HTTPException(
                status_code=400,
                detail="Please provide candidate_id or phone"
            )

        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")

        # Check consent
        has_consent = manager.has_valid_consent(candidate.id)

        return {
            "candidate_id": candidate.id,
            "has_valid_consent": has_consent,
            "consent_given": bool(candidate.consent_given),
            "consent_timestamp": candidate.consent_timestamp,
            "consent_method": candidate.consent_method,
            "consent_version": candidate.consent_version,
            "opted_out": bool(candidate.opted_out),
            "opted_out_at": candidate.opted_out_at,
            "data_retention_until": candidate.data_retention_until,
            "recording_consent": bool(candidate.recording_consent),
            "marketing_consent": bool(candidate.marketing_consent)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking consent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/retention/expired")
async def get_expired_retentions():
    """
    Get candidates whose data retention period has expired

    **Use case:** Admin endpoint to identify candidates requiring data deletion

    **Returns:** List of candidates with expired retention periods
    """
    try:
        manager = CandidateManager()
        candidates = manager.get_candidates_needing_deletion()

        return {
            "count": len(candidates),
            "candidates": [
                {
                    "id": c.id,
                    "name": c.name,
                    "phone": c.phone,
                    "data_retention_until": c.data_retention_until,
                    "days_expired": (
                        datetime.now() - datetime.fromisoformat(c.data_retention_until)
                    ).days if c.data_retention_until else None
                }
                for c in candidates
            ]
        }

    except Exception as e:
        logger.error(f"Error getting expired retentions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== Digital Consent Form Endpoints ==========

class DigitalSignatureRequest(BaseModel):
    """Request model for digital signature submission"""
    token: str
    signature: str
    consent_data_processing: bool
    consent_recording: bool = False
    consent_marketing: bool = False
    timestamp: str


@router.post("/consent/send-link")
async def send_consent_link(
    candidate_id: int = Body(...),
    email: str = Body(...),
    validity_days: int = Body(7)
):
    """
    Generate consent token and send link to candidate

    **Use case:** Send initial consent request email with secure link

    **Parameters:**
    - candidate_id: The candidate's ID
    - email: Candidate's email address
    - validity_days: Token validity (default: 7 days)

    **Returns:** Token and consent URL

    **Next step:** Send this URL via email to the candidate
    """
    try:
        manager = CandidateManager()
        candidate = manager.get_candidate(candidate_id=candidate_id)

        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")

        # Generate secure token
        token_manager = ConsentTokenManager()
        token = token_manager.generate_token(
            candidate_id=candidate_id,
            validity_days=validity_days
        )

        # Build consent URL
        consent_url = f"{settings.public_url}/gdpr/consent/form?token={token}"

        logger.info(f"Generated consent link for candidate {candidate_id}")

        return {
            "success": True,
            "message": "Consent link generated successfully",
            "candidate_id": candidate_id,
            "token": token,
            "consent_url": consent_url,
            "expires_in_days": validity_days,
            "email": email
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating consent link: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/consent/form", response_class=HTMLResponse)
async def show_consent_form(request: Request, token: str):
    """
    Display digital consent form

    **Use case:** Candidate clicks on consent link in email

    **Parameters:**
    - token: Secure consent token from email link

    **Returns:** HTML consent form with candidate data pre-filled
    """
    try:
        # Validate token
        token_manager = ConsentTokenManager()
        token_info = token_manager.validate_token(token)

        if not token_info:
            raise HTTPException(
                status_code=400,
                detail="Invalid or expired consent link. Please request a new link."
            )

        # Get candidate data
        manager = CandidateManager()
        candidate = manager.get_candidate(candidate_id=token_info['candidate_id'])

        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")

        # Render template
        return templates.TemplateResponse(
            "consent_form.html",
            {
                "request": request,
                "consent_token": token,
                "candidate_id": candidate.id,
                "candidate_name": candidate.name,
                "candidate_phone": candidate.phone,
                "candidate_email": candidate.email or "",
                "company_name": settings.company_name,
                "contact_email": settings.contact_email,
                "contact_phone": settings.contact_phone,
                "privacy_policy_url": settings.privacy_policy_url,
                "current_date": datetime.now().strftime("%d.%m.%Y")
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error displaying consent form: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/consent/submit-signature")
async def submit_digital_signature(
    request: Request,
    signature_data: DigitalSignatureRequest
):
    """
    Process digital signature and record consent

    **Use case:** Candidate submits signed consent form

    **Parameters:**
    - token: Consent token
    - signature: Candidate's typed name (digital signature)
    - consent_data_processing: Main consent checkbox
    - consent_recording: Optional recording consent
    - consent_marketing: Optional marketing consent
    - timestamp: Client-side timestamp

    **Returns:** Success confirmation
    """
    try:
        # Validate token
        token_manager = ConsentTokenManager()
        token_info = token_manager.validate_token(signature_data.token)

        if not token_info:
            raise HTTPException(
                status_code=400,
                detail="Invalid or expired consent link"
            )

        # Get candidate
        manager = CandidateManager()
        candidate = manager.get_candidate(candidate_id=token_info['candidate_id'])

        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")

        # Validate signature (basic check)
        if not signature_data.signature or len(signature_data.signature.strip()) < 3:
            raise HTTPException(
                status_code=400,
                detail="Invalid signature. Please provide your full name."
            )

        # Validate main consent
        if not signature_data.consent_data_processing:
            raise HTTPException(
                status_code=400,
                detail="Main consent is required"
            )

        # Get request metadata for audit trail
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        # Record consent in database
        success = manager.set_consent(
            candidate_id=candidate.id,
            consent_given=True,
            consent_method='web',
            consent_version='v1.0',
            recording_consent=signature_data.consent_recording,
            marketing_consent=signature_data.consent_marketing,
            retention_days=730  # 2 years
        )

        if not success:
            raise HTTPException(status_code=500, detail="Failed to record consent")

        # Mark token as used
        token_manager.mark_token_used(
            token=signature_data.token,
            ip_address=client_ip,
            user_agent=user_agent
        )

        # Log the consent
        logger.info(
            f"Digital consent recorded for candidate {candidate.id} "
            f"(signature: {signature_data.signature}, IP: {client_ip})"
        )

        # TODO: Send confirmation email to candidate

        return {
            "success": True,
            "message": "Consent successfully recorded",
            "candidate_id": candidate.id,
            "candidate_name": candidate.name,
            "consent_timestamp": datetime.now().isoformat(),
            "signature": signature_data.signature
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting digital signature: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== Token Management Endpoints ==========

@router.get("/tokens/stats")
async def get_token_statistics():
    """
    Get statistics about consent tokens

    **Use case:** Admin endpoint to monitor token usage

    **Returns:** Token statistics
    """
    try:
        token_manager = ConsentTokenManager()
        stats = token_manager.get_token_stats()

        return {
            "success": True,
            "statistics": stats,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting token stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tokens/cleanup")
async def cleanup_expired_tokens(days_old: int = Query(30)):
    """
    Clean up expired tokens

    **Use case:** Admin endpoint for token maintenance

    **Parameters:**
    - days_old: Delete tokens older than this (default: 30 days)

    **Returns:** Number of deleted tokens
    """
    try:
        token_manager = ConsentTokenManager()
        deleted_count = token_manager.cleanup_expired_tokens(days_old=days_old)

        return {
            "success": True,
            "message": f"Deleted {deleted_count} expired tokens",
            "deleted_count": deleted_count,
            "cutoff_days": days_old
        }

    except Exception as e:
        logger.error(f"Error cleaning up tokens: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== Health Check ==========

@router.get("/health")
async def gdpr_health_check():
    """Health check for GDPR API"""
    return {
        "status": "healthy",
        "service": "GDPR/DSGVO Compliance API",
        "timestamp": datetime.now().isoformat()
    }
