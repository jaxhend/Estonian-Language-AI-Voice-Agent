#!/usr/bin/env python3
"""
Create a test booking to show in the admin page
"""
import sys
import os
from uuid import uuid4

# Add the app to the path
sys.path.insert(0, os.path.dirname(__file__))

from app.services.booking_manager import create_booking, get_pending_bookings

def create_test_bookings():
    print("=" * 80)
    print("Creating Test Bookings for Admin Page")
    print("=" * 80)

    # Create a few test bookings
    test_bookings = [
        {
            "service_id": "haircut",
            "service_name": "Juukselõikus",
            "date_time": "2025-11-11 14:00",
            "location_id": "downtown",
            "location_name": "Kesklinnas",
            "customer_name": "Robin",
            "customer_phone": "+372 5256",
            "customer_email": "robin@example.com",
            "notes": "Eelistaks Maria teenindust"
        },
        {
            "service_id": "massage",
            "service_name": "Massaaž",
            "date_time": "2025-11-12 10:00",
            "location_id": "suburb",
            "location_name": "Kristiines",
            "customer_name": "Hendrik",
            "customer_phone": "+372 1234 5678",
            "customer_email": "hendrik@example.com",
            "notes": None
        },
        {
            "service_id": "consultation",
            "service_name": "Konsultatsioon",
            "date_time": "2025-11-09 15:30",
            "location_id": "downtown",
            "location_name": "Kesklinnas",
            "customer_name": "Maria",
            "customer_phone": "+372 9876 5432",
            "customer_email": None,
            "notes": "Esimene kord"
        }
    ]

    print(f"\nCreating {len(test_bookings)} test bookings...\n")

    created_count = 0
    for i, booking_data in enumerate(test_bookings, 1):
        booking_id = create_booking(
            client_id=uuid4(),
            **booking_data
        )

        if booking_id:
            created_count += 1
            print(f"{i}. ✅ {booking_data['customer_name']} - {booking_data['service_name']}")
            print(f"   ID: {booking_id[:8]}... | {booking_data['date_time']}")
        else:
            print(f"{i}. ❌ Failed to create booking for {booking_data['customer_name']}")

    print("\n" + "=" * 80)
    print(f"✅ Created {created_count}/{len(test_bookings)} test bookings")
    print("=" * 80)

    # Show pending bookings
    pending = get_pending_bookings()
    print(f"\n📋 Total pending bookings: {len(pending)}")

    print("\n🌐 Access the admin page:")
    print("   Frontend: http://localhost:5173/admin")
    print("   API: http://localhost:8000/api/bookings/pending")
    print("\n💡 The bookings should now appear in your admin page!")

if __name__ == "__main__":
    create_test_bookings()

