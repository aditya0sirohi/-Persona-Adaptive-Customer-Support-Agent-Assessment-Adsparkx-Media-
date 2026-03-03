from fastapi import FastAPI
from pydantic import BaseModel

from persona import detect_persona
from retriever import retrieve_context
from generator import generate_response
from escalation import check_escalation, create_handoff_packet

class ChatRequest(BaseModel):
	message: str

app = FastAPI()

@app.post("/chat")
def chat(request: ChatRequest):
	query = request.message

	persona, confidence = detect_persona(query)
	context, sources = retrieve_context(query)
	response = generate_response(query, persona, context)
	should_escalate, reason = check_escalation(query, response, persona)

	if should_escalate:
		handoff = create_handoff_packet(
			query=query,
			persona=persona,
			context=context,
			reason=reason
		)
		return {
			"persona": persona,
			"confidence": confidence,
			"escalation": True,
			"handoff_packet": handoff
		}

	return {
		"persona": persona,
		"confidence": confidence,
		"escalation": False,
		"response": response,
		"retrieved_sources": sources
	}
