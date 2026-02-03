"""
Speech-to-Text service using Whisper or stub implementation.
"""
import io
import logging
from typing import Optional

from backend.config import settings

logger = logging.getLogger(__name__)


class STTService:
    """Service for converting speech to text."""
    
    def __init__(self):
        self.use_stub = settings.USE_WHISPER_STUB
        self.model = None
        
        if not self.use_stub:
            try:
                import whisper
                self.model = whisper.load_model(settings.WHISPER_MODEL)
                logger.info(f"Loaded Whisper model: {settings.WHISPER_MODEL}")
            except ImportError:
                logger.warning("Whisper not installed. Using stub implementation.")
                self.use_stub = True
            except Exception as e:
                logger.error(f"Error loading Whisper model: {e}. Using stub.")
                self.use_stub = True
    
    async def transcribe(self, audio_data: bytes, content_type: str) -> str:
        """
        Transcribe audio data to text.
        
        Args:
            audio_data: Raw audio bytes
            content_type: MIME type of the audio (e.g., "audio/wav", "audio/mpeg")
        
        Returns:
            Transcribed text string
        """
        if self.use_stub:
            return self._transcribe_stub(audio_data, content_type)
        
        return await self._transcribe_whisper(audio_data, content_type)
    
    def _transcribe_stub(self, audio_data: bytes, content_type: str) -> str:
        """
        Stub implementation for testing without Whisper.
        Returns a sample transcription.
        """
        logger.info("Using stub STT implementation")
        # In a real scenario, you might want to return an error or use a different service
        # For now, return a placeholder that indicates the stub is being used
        return "This is a stub transcription. Please configure Whisper or set USE_WHISPER_STUB=false in your .env file."
    
    async def _transcribe_whisper(self, audio_data: bytes, content_type: str) -> str:
        """
        Transcribe using OpenAI Whisper.
        
        Args:
            audio_data: Raw audio bytes
            content_type: MIME type of the audio
        
        Returns:
            Transcribed text string
        """
        try:
            import whisper
            import tempfile
            import os
            
            # Save audio to temporary file
            # Whisper expects a file path, so we create a temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=self._get_file_extension(content_type)) as tmp_file:
                tmp_file.write(audio_data)
                tmp_path = tmp_file.name
            
            try:
                # Transcribe using Whisper
                result = self.model.transcribe(tmp_path)
                transcribed_text = result["text"].strip()
                
                logger.info(f"Transcribed {len(transcribed_text)} characters")
                return transcribed_text
            
            finally:
                # Clean up temp file
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
        
        except Exception as e:
            logger.error(f"Error in Whisper transcription: {e}")
            raise Exception(f"Transcription failed: {str(e)}")
    
    def _get_file_extension(self, content_type: str) -> str:
        """Get file extension from MIME type."""
        mime_to_ext = {
            "audio/wav": ".wav",
            "audio/wave": ".wav",
            "audio/x-wav": ".wav",
            "audio/mpeg": ".mp3",
            "audio/mp3": ".mp3",
            "audio/mp4": ".m4a",
            "audio/x-m4a": ".m4a",
            "audio/webm": ".webm",
            "audio/ogg": ".ogg",
            "audio/flac": ".flac",
        }
        return mime_to_ext.get(content_type.lower(), ".wav")
