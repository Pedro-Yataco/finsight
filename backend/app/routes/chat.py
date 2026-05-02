from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage

router = APIRouter()


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


class ChatResponse(BaseModel):
    reply: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: Request, body: ChatRequest):
    if not body.messages:
        raise HTTPException(status_code=400, detail="messages cannot be empty")

    graph = request.app.state.graph

    lc_messages = []
    for msg in body.messages:
        if msg.role == "user":
            lc_messages.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            lc_messages.append(AIMessage(content=msg.content))

    initial_state = {
        "messages": lc_messages,
        "ticker": None,
        "company_name": None,
        "raw_data": None,
        "derived_metrics": None,
        "analysis_complete": False,
    }

    result = await graph.ainvoke(initial_state)
    reply = result["messages"][-1].content
    return ChatResponse(reply=reply)
