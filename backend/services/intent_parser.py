"""
Intent and entity parsing service for extracting recipient names and email intent.
"""
import re
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class IntentParser:
    """Service for parsing intent and entities from transcribed text."""
    
    # Common email patterns
    RECIPIENT_PATTERNS = [
        r"(?:to|for|send|email|message)\s+(?:to\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
        r"(?:dear|hi|hello|hey)\s+([A-Z][a-z]+)",
        r"([A-Z][a-z]+\s+[A-Z][a-z]+)",  # Full name pattern
    ]
    
    INTENT_KEYWORDS = {
        "follow_up": ["follow up", "follow-up", "checking in", "touch base"],
        "meeting_request": ["meeting", "schedule", "call", "appointment", "meet"],
        "information_request": ["question", "ask", "need", "wondering", "inquire"],
        "thank_you": ["thank", "thanks", "appreciate", "grateful"],
        "apology": ["sorry", "apologize", "apology", "regret"],
        "introduction": ["introduce", "introduction", "meet", "new"],
        "reminder": ["remind", "reminder", "don't forget", "remember"],
    }
    
    def __init__(self):
        self.recipient_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.RECIPIENT_PATTERNS]
    
    async def parse(self, text: str) -> Dict[str, Optional[str]]:
        """
        Parse transcribed text to extract recipient name and intent.
        
        Args:
            text: The transcribed speech text
        
        Returns:
            Dictionary with recipient_name and intent
        """
        recipient_name = self._extract_recipient(text)
        intent = self._detect_intent(text)
        
        return {
            "recipient_name": recipient_name,
            "intent": intent,
            "confidence": "medium"  # Could be enhanced with ML model
        }
    
    def _extract_recipient(self, text: str) -> Optional[str]:
        """
        Extract recipient name from text using pattern matching.
        
        Args:
            text: The transcribed text
        
        Returns:
            Recipient name if found, None otherwise
        """
        for pattern in self.recipient_patterns:
            match = pattern.search(text)
            if match:
                name = match.group(1).strip()
                # Filter out common false positives
                if name.lower() not in ["email", "message", "send", "to"]:
                    logger.info(f"Extracted recipient name: {name}")
                    return name
        
        logger.info("No recipient name found in text")
        return None
    
    def _detect_intent(self, text: str) -> Optional[str]:
        """
        Detect email intent from keywords.
        
        Args:
            text: The transcribed text
        
        Returns:
            Detected intent or None
        """
        text_lower = text.lower()
        
        # Score each intent based on keyword matches
        intent_scores = {}
        for intent, keywords in self.INTENT_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                intent_scores[intent] = score
        
        if intent_scores:
            # Return intent with highest score
            detected_intent = max(intent_scores, key=intent_scores.get)
            logger.info(f"Detected intent: {detected_intent}")
            return detected_intent
        
        logger.info("No specific intent detected")
        return None
