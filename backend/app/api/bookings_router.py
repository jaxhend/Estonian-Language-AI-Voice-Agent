"""
HTTP routes for booking management
"""
from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel

from app.services.booking_manager import (
    get_pending_bookings,
    get_confirmed_bookings,
    get_cancelled_bookings,
    confirm_booking,
    cancel_booking,
    get_booking_by_id
)

router = APIRouter()


class BookingConfirmRequest(BaseModel):
    booking_id: str


class BookingCancelRequest(BaseModel):
    booking_id: str
    reason: str | None = None


@router.get("/bookings/pending")
async def list_pending_bookings():
    """Get all pending bookings"""
    bookings = get_pending_bookings()
    return {"bookings": bookings, "count": len(bookings)}


@router.get("/bookings/confirmed")
async def list_confirmed_bookings():
    """Get all confirmed bookings"""
    bookings = get_confirmed_bookings()
    return {"bookings": bookings, "count": len(bookings)}


@router.get("/bookings/cancelled")
async def list_cancelled_bookings():
    """Get all cancelled bookings"""
    bookings = get_cancelled_bookings()
    return {"bookings": bookings, "count": len(bookings)}


@router.get("/bookings/{booking_id}")
async def get_booking(booking_id: str):
    """Get a specific booking by ID"""
    booking = get_booking_by_id(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking


@router.post("/bookings/confirm")
async def confirm_booking_endpoint(request: BookingConfirmRequest):
    """Confirm a pending booking"""
    success = confirm_booking(request.booking_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to confirm booking")
    return {"message": "Booking confirmed successfully", "booking_id": request.booking_id}


@router.post("/bookings/cancel")
async def cancel_booking_endpoint(request: BookingCancelRequest):
    """Cancel a booking"""
    success = cancel_booking(request.booking_id, request.reason)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to cancel booking")
    return {"message": "Booking cancelled successfully", "booking_id": request.booking_id}

