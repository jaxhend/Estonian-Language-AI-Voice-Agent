from app.bus import bus
from app.schemas.events import STTFinal, ManagerRoute, AgentRequest

@bus.subscribe("stt.final")
async def on_stt_final(event: STTFinal):
    # TODO: Basic intent detection
    intent = "booking" # or "faq"
    agents = [intent]

    await bus.publish("manager.route", ManagerRoute(intent=intent, agents=agents, client_id=event.client_id))
    await bus.publish("agent.request", AgentRequest(agent=intent, text=event.text, client_id=event.client_id))
