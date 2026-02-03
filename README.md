# MailCrafter - Speech-to-Email Assistant

A voice-first AI assistant that converts speech to text, rewrites it professionally using Gemini API, auto-detects recipients, generates subjects, and sends emails securely.

## Features

- 🎤 **Speech-to-Text**: Convert audio input to text using Whisper
- ✍️ **Professional Email Rewriting**: Uses Gemini API to transform casual speech into professional emails
- 📧 **Auto Subject Generation**: Automatically generates appropriate subject lines
- 👥 **Recipient Resolution**: Resolves recipient names to email addresses from contacts
- 🔒 **Security-First**: Does not store email body content
- ♿ **Accessibility-Friendly**: Designed with blind and visually impaired users in mind

## Architecture

```
Voice Input → Speech-to-Text → Intent Parser → Gemini API → Recipient Resolver → SMTP Email Sender
```

### Components

- **Voice Input Layer**: Accepts audio files via FastAPI
- **STT Engine**: Whisper-based speech-to-text conversion
- **Intent & Entity Parser**: Extracts recipient names and email intent
- **Gemini Email Generator**: Rewrites text professionally and generates subjects
- **Recipient Resolver**: Looks up email addresses from contacts database
- **SMTP Email Service**: Sends emails securely via Gmail

## Setup Instructions

### Prerequisites

- Python 3.9 or higher
- Gmail account with App Password enabled
- Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone the repository** (if applicable) or navigate to the project directory:
   ```bash
   cd MailCrafter
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   # Copy the example env file
   cp backend/.env.example backend/.env
   
   # Edit backend/.env with your credentials
   ```

   Required environment variables:
   - `GEMINI_API_KEY`: Your Gemini API key
   - `GMAIL_USER`: Your Gmail address
   - `GMAIL_APP_PASSWORD`: Your Gmail App Password (16 characters)
   
   Optional:
   - `WHISPER_MODEL`: Whisper model size (default: "base")
   - `USE_WHISPER_STUB`: Set to "True" for testing without Whisper

5. **Get Gmail App Password**:
   - Go to [Google Account Settings](https://myaccount.google.com/)
   - Navigate to Security → 2-Step Verification → App Passwords
   - Generate a new app password for "Mail"
   - Copy the 16-character password to `GMAIL_APP_PASSWORD`

### Running the Server

```bash
# From the project root
python -m backend.main

# Or using uvicorn directly
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

API Documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Usage

### 1. Add Contacts

Before sending emails, add contacts to the database:

```bash
python -m backend.utils.manage_contacts add "John Doe" john.doe@example.com
python -m backend.utils.manage_contacts add "Jane Smith" jane@example.com

# List all contacts
python -m backend.utils.manage_contacts list
```

### 2. API Endpoints

#### Transcribe Audio
```bash
POST /api/v1/audio/transcribe
Content-Type: multipart/form-data

# Body: audio file (WAV, MP3, etc.)
```

Response:
```json
{
  "transcribed_text": "Hey John, I wanted to follow up on our meeting...",
  "recipient_name": "John",
  "intent": "follow_up",
  "raw_intent_data": {...}
}
```

#### Generate Email
```bash
POST /api/v1/email/generate
Content-Type: application/json

{
  "transcribed_text": "Hey John, I wanted to follow up...",
  "recipient_name": "John",
  "intent": "follow_up"
}
```

Response:
```json
{
  "success": true,
  "message": "Email generated successfully",
  "email_body": "Dear John,\n\nI hope this email finds you well...",
  "subject": "Follow-up on Our Recent Meeting"
}
```

#### Send Email
```bash
POST /api/v1/email/send
Content-Type: application/json

{
  "transcribed_text": "...",
  "recipient_name": "John",
  "intent": "follow_up",
  "email_body": "Dear John,...",
  "subject": "Follow-up on Our Recent Meeting"
}
```

#### Complete Flow (Process and Send)
```bash
POST /api/v1/email/process-and-send
Content-Type: application/json

{
  "transcribed_text": "Hey John, I wanted to follow up...",
  "recipient_name": "John",
  "intent": "follow_up"
}
```

### 3. Example cURL Requests

```bash
# Transcribe audio
curl -X POST "http://localhost:8000/api/v1/audio/transcribe" \
  -F "audio_file=@recording.wav"

# Generate and send email
curl -X POST "http://localhost:8000/api/v1/email/process-and-send" \
  -H "Content-Type: application/json" \
  -d '{
    "transcribed_text": "Hey John, can we schedule a meeting next week?",
    "recipient_name": "John",
    "intent": "meeting_request"
  }'
```

## Project Structure

```
MailCrafter/
├── backend/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management
│   ├── .env                    # Environment variables (not in git)
│   ├── .env.example            # Example environment file
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── audio.py            # Audio transcription routes
│   │   └── email.py            # Email generation and sending routes
│   ├── services/
│   │   ├── __init__.py
│   │   ├── stt_service.py      # Speech-to-text service
│   │   ├── intent_parser.py    # Intent and entity extraction
│   │   ├── gemini_service.py   # Gemini API integration
│   │   ├── email_service.py    # SMTP email sending
│   │   └── recipient_resolver.py # Contact lookup service
│   ├── utils/
│   │   ├── __init__.py
│   │   └── manage_contacts.py  # Contact management utility
│   └── data/
│       └── contacts.db          # SQLite database (created automatically)
├── requirements.txt
└── README.md
```

## Security Considerations

- ✅ **No Email Storage**: Email body content is never stored in the database
- ✅ **Environment Variables**: All secrets loaded from `.env` file
- ✅ **App Passwords**: Uses Gmail App Passwords instead of main password
- ✅ **Input Validation**: File size and type validation
- ✅ **Error Handling**: Comprehensive error handling without exposing sensitive info

## Development Notes

### Testing Without Whisper

Set `USE_WHISPER_STUB=True` in `.env` to use a stub implementation for testing without installing Whisper.

### Installing Whisper (Optional)

`openai-whisper` can fail to install on very new Python versions (for example Python 3.14).
If you hit build errors, keep `USE_WHISPER_STUB=True` and test the rest of the pipeline.
To enable real STT later, install Whisper in a Python version where it builds (commonly Python 3.10–3.12),
then set `USE_WHISPER_STUB=False`.

### Whisper Model Sizes

- `tiny`: Fastest, least accurate
- `base`: Good balance (default)
- `small`: Better accuracy
- `medium`: High accuracy
- `large`: Best accuracy, slowest

### Gemini Prompts

The service uses carefully crafted prompts for:
1. **Email Rewriting**: Converts casual speech to professional email format
2. **Subject Generation**: Creates concise, professional subject lines

See `backend/services/gemini_service.py` for prompt details.

## Troubleshooting

### "GEMINI_API_KEY not set"
- Ensure `backend/.env` exists and contains `GEMINI_API_KEY=your_key`

### "SMTP authentication failed"
- Verify `GMAIL_USER` and `GMAIL_APP_PASSWORD` are correct
- Ensure 2-Step Verification is enabled on your Google account
- Generate a new App Password if needed

### "Recipient email not found"
- Add the contact using: `python -m backend.utils.manage_contacts add "Name" email@example.com`
- Check the name matches what was extracted from the transcription

### Whisper Installation Issues
- On some systems, you may need: `pip install --upgrade --no-deps --force-reinstall openai-whisper`
- Or use `USE_WHISPER_STUB=True` for testing

## Future Enhancements

- [ ] Frontend microphone UI
- [ ] Rate limiting
- [ ] OAuth integration for Gmail
- [ ] Support for multiple email providers
- [ ] Email templates
- [ ] Voice feedback for accessibility
- [ ] Batch email processing

## License

This project is provided as-is for educational and development purposes.

## Contributing

Contributions are welcome! Please ensure:
- Code follows PEP 8 style guidelines
- Security best practices are maintained
- Accessibility considerations are included
