"""
Audio processing routes for speech-to-text conversion.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from backend.services.stt_service import STTService
from backend.services.intent_parser import IntentParser
from backend.config import settings

router = APIRouter()
stt_service = STTService()
intent_parser = IntentParser()


@router.post("/audio/transcribe")
async def transcribe_audio(audio_file: UploadFile = File(...)):
    """
    Accept audio input and convert to text.
    
    Returns:
        - transcribed_text: The speech-to-text result
        - recipient_name: Extracted recipient name (if found)
        - intent: Email intent/purpose
    """
    # Validate file type
    if not audio_file.content_type or not audio_file.content_type.startswith("audio/"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload an audio file."
        )
    
    # Validate file size
    contents = await audio_file.read()
    file_size_mb = len(contents) / (1024 * 1024)
    
    if file_size_mb > settings.MAX_AUDIO_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.MAX_AUDIO_SIZE_MB}MB"
        )
    
    try:
        # Convert speech to text
        transcribed_text = await stt_service.transcribe(contents, audio_file.content_type)
        print("TRANSCRIBED:", transcribed_text)
        
        if not transcribed_text or not transcribed_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not transcribe audio. Please ensure the audio contains clear speech."
            )
        
        # Extract recipient name and intent
        intent_data = await intent_parser.parse(transcribed_text)
        
        return JSONResponse(
            status_code=200,
            content={
                "transcribed_text": transcribed_text,
                "recipient_name": intent_data.get("recipient_name"),
                "intent": intent_data.get("intent"),
                "raw_intent_data": intent_data
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing audio: {str(e)}"
        )
