import httpx
# app/llm/agents/booking.py
import os

from app.bus import bus
from app.core.ids import new_id
from app.schemas.events import AgentRequest, AgentResult, ManagerAnswer
from app.services.booking_manager import create_booking, format_booking_confirmation
from app.services.context_loader import format_context_for_llm, search_faq
from app.services.conversation_history import format_history_for_llm, add_message_to_history

from .base import Agent
from ...core import config

# Load business context once at import
BUSINESS_CONTEXT = format_context_for_llm()

SYSTEM_PROMPT = f"""Sa oled abivalmis eestikeelne AI assistent broneerimissüsteemi jaoks.
Sa aitad kasutajatel broneerida aegu, vastata teenuste kohta küsimustele ja pakkuda abi.

OLULINE KONTEKST SINU ETTEVÕTTE KOHTA:
{BUSINESS_CONTEXT}

BRONEERIMISE PROTSESS:
1. Küsi kasutajalt, millist teenust ta soovib (haircut/massage/consultation)
2. Küsi soovitud aega ja kuupäeva
3. Küsi soovitud asukohta (downtown/suburb)
4. Küsi kliendi nimi
5. Küsi kliendi kontakttelefon
6. AINULT SIIS kui KÕIK 5 andmed on kogutud, korda üle kõik detailid
7. Küsi kinnitust: "Kas kinnitate broneeringu?"
8. AINULT SIIS kui kasutaja kinnitab JA kõik andmed on olemas, kasuta BOOKING_CONFIRMED märgendit

TÄHTIS - ENNE BOOKING_CONFIRMED KASUTAMIST:
✓ Teenus peab olema valitud (haircut/massage/consultation)
✓ Kuupäev ja kellaaeg peavad olema teada
✓ Asukoht peab olema valitud (downtown=Kesklinnas või suburb=Kristiines)
✓ Kliendi nimi peab olema teada
✓ Kliendi telefon peab olema teada
✓ Kasutaja peab olema kinnitanud

TÄHTIS - KUUPÄEVA FORMAAT:
- Kasuta ALATI aastat 2025
- Formaat: YYYY-MM-DD HH:MM
- Näiteks: 2025-11-09 14:00, 2025-12-15 10:00
- Kui kasutaja ütleb "homme", "järgmine nädal", arvuta õige kuupäev aastas 2025

PRAEGUNE KUUPÄEV: 8. november 2025

OLULINE: AINULT kui KÕIK andmed on kogutud JA kasutaja kinnitab, 
lisa oma vastuse LÕPPU täpselt see märgend formaadis:
BOOKING_CONFIRMED|teenus_id|teenus_nimi|kuupäev_ja_kellaaeg|asukoht_id|asukoht_nimi|kliendi_nimi|telefon|märkused

Näide õigest protsessist:
1. Kasutaja: "Tahan broneerida juukselõikuse"
2. AI: "Millisel ajal?"
3. Kasutaja: "Homme kell 14:00"
4. AI: "Kas Kesklinnas või Kristiines?"
5. Kasutaja: "Kesklinnas"
6. AI: "Palun andke oma nimi"
7. Kasutaja: "Robin"
8. AI: "Ja teie kontakttelefon?"
9. Kasutaja: "5256"
10. AI: "Kas kinnitate: Juukselõikus homme kell 14:00 Kesklinnas, Robin, tel 5256?"
11. Kasutaja: "Jah"
12. AI: "Suurepärane!" BOOKING_CONFIRMED|haircut|Juukselõikus|2025-11-09 14:00|downtown|Kesklinnas|Robin|5256|

JUHISED:
- Kasuta ülaltoodud konteksti, et vastata küsimustele täpselt ja informatiivselt
- Kui kasutaja küsib teenuste, hindade, lahtiolekuaegade või asukohtade kohta, kasuta ülaltoodud infot
- Kui sa näed eelmist vestlust, kasuta seda konteksti oma vastuse jaoks
- Kui kasutaja viitab millelegi varasemast vestlusest, kasuta seda teavet
- Ole sõbralik, professionaalne ja lühike
- Vasta eesti keeles, kui kasutaja räägib eesti keeles
- Vasta inglise keeles, kui kasutaja räägib inglise keeles"""


class BookingAgent(Agent):
    async def process(self, event: AgentRequest):
        try:
            # Get conversation history for context
            conversation_history = format_history_for_llm(event.client_id, limit=5)

            # First, check if this is a FAQ question
            faq_answer = search_faq(event.text)

            # Generate LLM response using vLLM
            print(f"🤖 Generating LLM response for: '{event.text}'")
            if conversation_history:
                print(f"📜 Including conversation history ({len(conversation_history.split('Kasutaja:')) - 1} exchanges)")

            # Create prompt with system context, history, and user message
            full_prompt = f"{SYSTEM_PROMPT}\n\n"

            # Add conversation history if available
            if conversation_history:
                full_prompt += f"{conversation_history}\n"

            # Add FAQ answer if found
            if faq_answer:
                full_prompt += f"LEITUD FAQ VASTUS: {faq_answer}\n\n"

            full_prompt += f"Kasutaja: {event.text}\n\nAssistent:"

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    config.LLM_URL,
                    headers={"Content-Type": "application/json"},
                    json={
                        "model": config.LLM_MODEL,
                        "prompt": full_prompt,
                        "max_tokens": 250,
                        "temperature": 0.7,
                        "stop": ["\n\nKasutaja:", "Kasutaja:"]
                    }
                )
                response.raise_for_status()
                data = response.json()

            response_text = data["choices"][0]["text"].strip()
            print(f"🤖 LLM generated response: '{response_text}'")

            # Check if response contains booking confirmation marker
            booking_created = False
            if "BOOKING_CONFIRMED|" in response_text:
                # Extract booking details
                parts = response_text.split("BOOKING_CONFIRMED|")
                if len(parts) > 1:
                    booking_data = parts[1].split("|")
                    if len(booking_data) >= 7:
                        service_id, service_name, date_time, location_id, location_name, customer_name, customer_phone = booking_data[:7]
                        notes = booking_data[8] if len(booking_data) > 8 else ""

                        # Create the booking
                        booking_id = create_booking(
                            client_id=event.client_id,
                            service_id=service_id.strip(),
                            service_name=service_name.strip(),
                            date_time=date_time.strip(),
                            location_id=location_id.strip(),
                            location_name=location_name.strip(),
                            customer_name=customer_name.strip(),
                            customer_phone=customer_phone.strip(),
                            notes=notes.strip() if notes else None
                        )

                        if booking_id:
                            booking_created = True
                            print(f"📅 Booking created: {booking_id}")
                            # Remove the marker from response
                            response_text = parts[0].strip()
                            # Add confirmation message
                            response_text += f"\n\nTeie broneering on salvestatud ja ootab kinnitust. Broneeringu number: {booking_id[:8]}"

            # Save this exchange to conversation history
            saved = add_message_to_history(event.client_id, event.text, response_text)
            if saved:
                print(f"💾 Conversation saved to history")

            # Send the result to the manager
            await bus.publish("agent.result", AgentResult(
                agent="booking",
                result={
                    "response": response_text,
                    "status": "completed",
                    "context_used": bool(faq_answer),
                    "history_used": bool(conversation_history),
                    "booking_created": booking_created
                },
                confidence=0.9,
                client_id=event.client_id
            ))

            # Send the response to the client via TTS
            await bus.publish("manager.answer", ManagerAnswer(
                text=response_text,
                trace_id=new_id("trace"),
                client_id=event.client_id
            ))

        except Exception as e:
            print(f"❌ Error in BookingAgent: {e}")
            import traceback
            traceback.print_exc()
            # Fallback response if LLM fails
            fallback_text = "Vabandust, mul tekkis viga. Palun proovi uuesti."
            await bus.publish("manager.answer", ManagerAnswer(
                text=fallback_text,
                trace_id=new_id("trace"),
                client_id=event.client_id
            ))

@bus.subscribe("agent.request")
async def on_agent_request(event: AgentRequest):
    if event.agent == "booking":
        agent = BookingAgent()
        await agent.process(event)

