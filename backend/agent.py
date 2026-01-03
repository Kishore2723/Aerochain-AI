import os
import base64
from dotenv import load_dotenv
from typing import AsyncIterable, Optional
from fastapi import UploadFile
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

# THE SYSTEM PROMPT - ANTIGRAVITY PERSONA
SYSTEM_PROMPT = """ROLE:
You are AeroChain, an AI intelligence engine designed for speed and precision.

MISSION:
Provide expert, high-velocity assistance. Eliminate friction. Be helpful, but concise.

GUIDELINES:
1. **Directness**: Answer the user's question immediately. Minimize preamble.
2. **Clarity**: Use clear, technical language. Format code blocks precisely.
3. **Efficiency**: Do not withhold information, but avoid unnecessary fluff.
4. **Context**: You are running in the "Antigravity" interface—a high-performance, linear-log environment.
5. **Multimodal**: If you receive an image or file, analyze it instantly and answer the user's query about it.

Your goal is to be the fastest path from question to answer."""

def get_llm():
    """Selects the LLM provider based on available API keys."""
    google_api_key = os.getenv("GOOGLE_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_base_url = os.getenv("OPENAI_BASE_URL")

    if google_api_key:
        return ChatGoogleGenerativeAI(
            model="gemini-1.5-flash", 
            google_api_key=google_api_key,
            temperature=0,
            convert_system_message_to_human=True
        )
    elif openai_api_key:
        return ChatOpenAI(
            api_key=openai_api_key,
            base_url=openai_base_url,
            model="gpt-4o-mini",
            temperature=0
        )
    else:
        raise ValueError("No valid API Key found (OPENAI_API_KEY or GOOGLE_API_KEY).")

async def process_file(file: UploadFile) -> dict:
    """Reads a file and returns a dict suitable for LangChain content"""
    content = await file.read()
    encoded = base64.b64encode(content).decode("utf-8")
    
    # Simple media type detection
    text_types = ["text/plain", "text/markdown", "text/csv", "application/json"]
    
    if file.content_type in text_types or file.filename.endswith(('.txt', '.md', '.py', '.js', '.json')):
        return {"type": "text", "text": f"\n\n[FILE START: {file.filename}]\n{content.decode('utf-8', errors='ignore')}\n[FILE END]\n\n"}
    else:
        # Assume image for others (Gemini/GPT-4V can handle it)
        return {
            "type": "image_url",
            "image_url": {"url": f"data:{file.content_type};base64,{encoded}"}
        }

async def generate_response(message: str, file: Optional[UploadFile] = None) -> AsyncIterable[str]:
    """Generates a streaming response using LangChain with optional file context."""
    
    try:
        llm = get_llm()
        
        messages = [SystemMessage(content=SYSTEM_PROMPT)]
        
        user_content = [{"type": "text", "text": message}]
        
        if file:
            file_data = await process_file(file)
            user_content.append(file_data)
        
        messages.append(HumanMessage(content=user_content))
        
        async for chunk in llm.astream(messages):
            if hasattr(chunk, 'content'):
                yield chunk.content
            elif isinstance(chunk, str):
                yield chunk

    except Exception as e:
        yield f"ANTIGRAVITY_FAILURE: {str(e)}"
