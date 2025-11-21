"""
GDPR/DSGVO API endpoints for candidate data management
Implements data subject rights: access, rectification, erasure, portability, restriction
"""

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict
from datetime import datetime
import json

from src.candidate_manager import CandidateManager
from loguru import logger

router = APIRouter(prefix="/gdpr", tags=["GDPR/DSGVO"])


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


# ========== Health Check ==========

@router.get("/health")
async def gdpr_health_check():
    """Health check for GDPR API"""
    return {
        "status": "healthy",
        "service": "GDPR/DSGVO Compliance API",
        "timestamp": datetime.now().isoformat()
    }
