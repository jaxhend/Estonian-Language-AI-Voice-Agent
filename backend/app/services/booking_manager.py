"""
Booking manager for handling appointment bookings
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4

CONTEXT_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "context_database.json")

def load_database() -> Dict[str, Any]:
    """Load the entire database"""
    try:
        with open(CONTEXT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading database: {e}")
        return {}

def save_database(data: Dict[str, Any]) -> bool:
    """Save the entire database"""
    try:
        with open(CONTEXT_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving database: {e}")
        return False

def create_booking(
    client_id: UUID,
    service_id: str,
    service_name: str,
    date_time: str,
    location_id: str,
    location_name: str,
    customer_name: str,
    customer_phone: str,
    customer_email: Optional[str] = None,
    notes: Optional[str] = None
) -> Optional[str]:
    """
    Create a new pending booking

    Returns:
        booking_id if successful, None otherwise
    """
    db = load_database()

    if "bookings" not in db:
        db["bookings"] = {
            "pending": [],
            "confirmed": [],
            "cancelled": []
        }

    booking_id = str(uuid4())

    booking = {
        "booking_id": booking_id,
        "client_id": str(client_id),
        "service_id": service_id,
        "service_name": service_name,
        "date_time": date_time,
        "location_id": location_id,
        "location_name": location_name,
        "customer_name": customer_name,
        "customer_phone": customer_phone,
        "customer_email": customer_email,
        "notes": notes,
        "created_at": datetime.now().isoformat(),
        "status": "pending"
    }

    db["bookings"]["pending"].append(booking)

    if save_database(db):
        print(f"✅ Booking {booking_id} created and added to pending list")
        return booking_id
    return None

def get_pending_bookings() -> List[Dict[str, Any]]:
    """Get all pending bookings"""
    db = load_database()
    return db.get("bookings", {}).get("pending", [])

def get_confirmed_bookings() -> List[Dict[str, Any]]:
    """Get all confirmed bookings"""
    db = load_database()
    return db.get("bookings", {}).get("confirmed", [])

def get_cancelled_bookings() -> List[Dict[str, Any]]:
    """Get all cancelled bookings"""
    db = load_database()
    return db.get("bookings", {}).get("cancelled", [])

def get_booking_by_id(booking_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific booking by ID"""
    db = load_database()
    bookings = db.get("bookings", {})

    # Search in all categories
    for category in ["pending", "confirmed", "cancelled"]:
        for booking in bookings.get(category, []):
            if booking.get("booking_id") == booking_id:
                return booking

    return None

def confirm_booking(booking_id: str) -> bool:
    """
    Move a booking from pending to confirmed

    Returns:
        True if successful, False otherwise
    """
    db = load_database()
    bookings = db.get("bookings", {})

    # Find and remove from pending
    booking = None
    for i, b in enumerate(bookings.get("pending", [])):
        if b.get("booking_id") == booking_id:
            booking = bookings["pending"].pop(i)
            break

    if not booking:
        print(f"❌ Booking {booking_id} not found in pending")
        return False

    # Update status and add to confirmed
    booking["status"] = "confirmed"
    booking["confirmed_at"] = datetime.now().isoformat()
    bookings["confirmed"].append(booking)

    if save_database(db):
        print(f"✅ Booking {booking_id} confirmed")
        return True
    return False

def cancel_booking(booking_id: str, reason: Optional[str] = None) -> bool:
    """
    Cancel a booking (move to cancelled)

    Returns:
        True if successful, False otherwise
    """
    db = load_database()
    bookings = db.get("bookings", {})

    # Find and remove from pending or confirmed
    booking = None
    for category in ["pending", "confirmed"]:
        for i, b in enumerate(bookings.get(category, [])):
            if b.get("booking_id") == booking_id:
                booking = bookings[category].pop(i)
                break
        if booking:
            break

    if not booking:
        print(f"❌ Booking {booking_id} not found")
        return False

    # Update status and add to cancelled
    booking["status"] = "cancelled"
    booking["cancelled_at"] = datetime.now().isoformat()
    if reason:
        booking["cancellation_reason"] = reason
    bookings["cancelled"].append(booking)

    if save_database(db):
        print(f"✅ Booking {booking_id} cancelled")
        return True
    return False

def get_bookings_by_client(client_id: UUID) -> List[Dict[str, Any]]:
    """Get all bookings for a specific client"""
    db = load_database()
    bookings = db.get("bookings", {})
    client_id_str = str(client_id)

    result = []
    for category in ["pending", "confirmed", "cancelled"]:
        for booking in bookings.get(category, []):
            if booking.get("client_id") == client_id_str:
                result.append(booking)

    return result

def format_booking_confirmation(booking_id: str) -> str:
    """Format a booking confirmation message"""
    booking = get_booking_by_id(booking_id)

    if not booking:
        return "Broneeringut ei leitud."

    status_et = {
        "pending": "Ootel",
        "confirmed": "Kinnitatud",
        "cancelled": "Tühistatud"
    }

    msg = f"""
BRONEERING #{booking_id[:8]}
Status: {status_et.get(booking['status'], booking['status'])}

Teenus: {booking['service_name']}
Aeg: {booking['date_time']}
Asukoht: {booking['location_name']}

Klient: {booking['customer_name']}
Telefon: {booking['customer_phone']}
"""

    if booking.get('customer_email'):
        msg += f"E-post: {booking['customer_email']}\n"

    if booking.get('notes'):
        msg += f"\nMärkused: {booking['notes']}\n"

    return msg.strip()

