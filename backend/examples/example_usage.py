"""
Example usage of the MailCrafter API.

This script demonstrates how to use the API endpoints programmatically.
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"


def example_transcribe_audio(audio_file_path: str):
    """Example: Transcribe an audio file."""
    print("📤 Transcribing audio file...")
    
    with open(audio_file_path, 'rb') as f:
        files = {'audio_file': f}
        response = requests.post(f"{BASE_URL}/audio/transcribe", files=files)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Transcription: {data['transcribed_text']}")
        print(f"✓ Recipient: {data.get('recipient_name', 'Not found')}")
        print(f"✓ Intent: {data.get('intent', 'Not detected')}")
        return data
    else:
        print(f"✗ Error: {response.status_code} - {response.text}")
        return None


def example_generate_email(transcribed_text: str, recipient_name: str = None, intent: str = None):
    """Example: Generate professional email using Gemini."""
    print("\n📝 Generating professional email...")
    
    payload = {
        "transcribed_text": transcribed_text,
        "recipient_name": recipient_name,
        "intent": intent
    }
    
    response = requests.post(
        f"{BASE_URL}/email/generate",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Subject: {data['subject']}")
        print(f"✓ Email Body:\n{data['email_body']}")
        return data
    else:
        print(f"✗ Error: {response.status_code} - {response.text}")
        return None


def example_send_email(transcribed_text: str, email_body: str, subject: str, recipient_name: str = None):
    """Example: Send email."""
    print("\n📧 Sending email...")
    
    payload = {
        "transcribed_text": transcribed_text,
        "recipient_name": recipient_name,
        "email_body": email_body,
        "subject": subject
    }
    
    response = requests.post(
        f"{BASE_URL}/email/send",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Email sent successfully!")
        print(f"✓ To: {data['recipient_email']}")
        print(f"✓ Subject: {data['subject']}")
        return data
    else:
        print(f"✗ Error: {response.status_code} - {response.text}")
        return None


def example_complete_flow(transcribed_text: str, recipient_name: str = None, intent: str = None):
    """Example: Complete flow - generate and send in one request."""
    print("\n🚀 Complete flow: Generate and send email...")
    
    payload = {
        "transcribed_text": transcribed_text,
        "recipient_name": recipient_name,
        "intent": intent
    }
    
    response = requests.post(
        f"{BASE_URL}/email/process-and-send",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Email processed and sent successfully!")
        print(f"✓ To: {data['recipient_email']}")
        print(f"✓ Subject: {data['subject']}")
        return data
    else:
        print(f"✗ Error: {response.status_code} - {response.text}")
        return None


if __name__ == "__main__":
    print("=" * 60)
    print("MailCrafter API - Example Usage")
    print("=" * 60)
    
    # Example 1: Generate email (without sending)
    example_text = "Hey John, I wanted to follow up on our meeting yesterday. Can we schedule another call this week?"
    
    result = example_generate_email(
        transcribed_text=example_text,
        recipient_name="John",
        intent="follow_up"
    )
    
    # Example 2: Complete flow (generate and send)
    # Uncomment to test (requires valid contact in database)
    # example_complete_flow(
    #     transcribed_text=example_text,
    #     recipient_name="John",
    #     intent="follow_up"
    # )
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)
