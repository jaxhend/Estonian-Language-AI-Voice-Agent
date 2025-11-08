#!/usr/bin/env python3
"""
Add bookings section to context database
"""
import json
import os

context_file = "context_database.json"

try:
    # Load existing data
    with open(context_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Add bookings section if not exists
    if "bookings" not in data:
        data["bookings"] = {
            "pending": [],
            "confirmed": [],
            "cancelled": []
        }
        print("✅ Added bookings section")
    else:
        print("ℹ️ Bookings section already exists")

    # Save updated data
    with open(context_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("✅ Database updated successfully")
    print(f"Keys in database: {list(data.keys())}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

