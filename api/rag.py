import traceback
from fastapi import APIRouter, HTTPException, Request
from app.schemes.rag import RequestChatSchema, ResponseChatSchema
from app.services.rag_services import handle_chat_request

router = APIRouter()

@router.post("/chat", response_model=ResponseChatSchema)
async def chat_endpoint(request: Request, payload: RequestChatSchema) -> ResponseChatSchema:
    try:
        result = await handle_chat_request(
            redis=request.app.state.redis,
            vectorstore=request.app.state.vectorstore,
            session_id=payload.session_id,
            query=payload.query,
        )
        return ResponseChatSchema(**result)
    except Exception:
        traceback.print_exc() # log lai traceback garxa   
        raise HTTPException(status_code=500, detail="Internal server error")
