"""
Context loader utility for loading business data from JSON file
"""
import json
import os
from typing import Dict, Any

_context_cache: Dict[str, Any] = {}

def load_context() -> Dict[str, Any]:
    """Load the context database from JSON file"""
    global _context_cache

    if _context_cache:
        return _context_cache

    context_file = os.path.join(os.path.dirname(__file__), "..", "..", "context_database.json")

    try:
        with open(context_file, 'r', encoding='utf-8') as f:
            _context_cache = json.load(f)
        return _context_cache
    except FileNotFoundError:
        print(f"Warning: Context database file not found: {context_file}")
        return {}
    except Exception as e:
        print(f"Error loading context database: {e}")
        return {}

def format_context_for_llm() -> str:
    """Format the context data into a readable string for the LLM"""
    context = load_context()

    if not context:
        return "No business context available."

    parts = []

    # Business info
    if "business" in context:
        biz = context["business"]
        parts.append(f"ETTEVÕTE: {biz.get('name', 'N/A')}")
        parts.append(f"Kirjeldus: {biz.get('description', 'N/A')}")
        parts.append(f"Telefon: {biz.get('phone', 'N/A')}")
        parts.append(f"E-post: {biz.get('email', 'N/A')}")
        parts.append("")

    # Services
    if "services" in context:
        parts.append("TEENUSED:")
        for svc in context["services"]:
            if svc.get("available", True):
                parts.append(f"- {svc['name']}: {svc['description']} ({svc['duration_minutes']}min, {svc['price_eur']}€)")
        parts.append("")

    # Working hours
    if "working_hours" in context:
        parts.append("LAHTIOLEKUAJAD:")
        hours = context["working_hours"]
        days_et = {
            "monday": "Esmaspäev",
            "tuesday": "Teisipäev",
            "wednesday": "Kolmapäev",
            "thursday": "Neljapäev",
            "friday": "Reede",
            "saturday": "Laupäev",
            "sunday": "Pühapäev"
        }
        for day_en, day_et in days_et.items():
            if day_en in hours:
                if hours[day_en].get("closed"):
                    parts.append(f"- {day_et}: Suletud")
                else:
                    parts.append(f"- {day_et}: {hours[day_en]['open']}-{hours[day_en]['close']}")
        parts.append("")

    # Locations
    if "locations" in context:
        parts.append("ASUKOHAD:")
        for loc in context["locations"]:
            if loc.get("available", True):
                parts.append(f"- {loc['name']}: {loc['address']}")
        parts.append("")

    # Staff
    if "staff" in context:
        parts.append("PERSONAL:")
        for staff in context["staff"]:
            specialties = ", ".join(staff.get("specialties", []))
            parts.append(f"- {staff['name']}: {specialties}")
        parts.append("")

    # Policies
    if "policies" in context:
        pol = context["policies"]
        parts.append("REEGLID:")
        parts.append(f"- Tühistamine: vähemalt {pol.get('cancellation_hours', 24)}h ette")
        parts.append(f"- Hilinemine: max {pol.get('late_arrival_minutes', 15)} minutit")
        parts.append(f"- Broneering: kuni {pol.get('advance_booking_days', 30)} päeva ette")
        parts.append("")

    return "\n".join(parts)

def get_faq() -> list:
    """Get FAQ entries"""
    context = load_context()
    return context.get("faq", [])

def search_faq(query: str) -> str:
    """Search FAQ for relevant answers"""
    query_lower = query.lower()
    faqs = get_faq()

    # Simple keyword matching
    for faq in faqs:
        question = faq.get("question", "").lower()
        if any(word in question for word in query_lower.split()):
            return faq.get("answer", "")

    return ""

