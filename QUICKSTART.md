# Quick Start Guide

Get MailCrafter up and running in 5 minutes!

## Step 1: Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

## Step 2: Configure Environment

1. Copy the example environment file:
   ```bash
   copy backend\.env.example backend\.env
   ```

2. Edit `backend\.env` and add your credentials:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   GMAIL_USER=your.email@gmail.com
   GMAIL_APP_PASSWORD=your_16_char_app_password
   ```

3. For first-time testing, keep Whisper in **stub mode**:
   ```env
   USE_WHISPER_STUB=True
   ```

4. Get your Gmail App Password:
   - Go to https://myaccount.google.com/apppasswords
   - Generate a new app password for "Mail"
   - Copy the 16-character password

5. Get your Gemini API Key:
   - Go to https://makersuite.google.com/app/apikey
   - Create a new API key
   - Copy it to `GEMINI_API_KEY`

## Step 3: Add a Contact

Before sending emails, add at least one contact:

```bash
python -m backend.utils.manage_contacts add "John Doe" john.doe@example.com
```

Verify it was added:
```bash
python -m backend.utils.manage_contacts list
```

## Step 4: Start the Server

```bash
python -m backend.main
```

Or with uvicorn:
```bash
uvicorn backend.main:app --reload
```

The API will be available at `http://localhost:8000`

## Step 5: Test the API

### Option A: Using the API Documentation

1. Open your browser: http://localhost:8000/docs
2. Try the `/api/v1/email/generate` endpoint with:
   ```json
   {
     "transcribed_text": "Hey John, can we schedule a meeting next week?",
     "recipient_name": "John",
     "intent": "meeting_request"
   }
   ```

### Option B: Using cURL

```bash
curl -X POST "http://localhost:8000/api/v1/email/generate" \
  -H "Content-Type: application/json" \
  -d "{\"transcribed_text\": \"Hey John, can we schedule a meeting next week?\", \"recipient_name\": \"John\", \"intent\": \"meeting_request\"}"
```

### Option C: Using Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/email/generate",
    json={
        "transcribed_text": "Hey John, can we schedule a meeting next week?",
        "recipient_name": "John",
        "intent": "meeting_request"
    }
)

print(response.json())
```

## Troubleshooting

### "Module not found" errors
- Make sure you're in the project root directory
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again

### "GEMINI_API_KEY not set"
- Check that `backend\.env` exists (not `.env.example`)
- Verify the file contains `GEMINI_API_KEY=your_key` (no spaces around `=`)

### "SMTP authentication failed"
- Verify your Gmail App Password is correct (16 characters, no spaces)
- Ensure 2-Step Verification is enabled on your Google account
- Try generating a new App Password

### "Recipient email not found"
- Add the contact first: `python -m backend.utils.manage_contacts add "Name" email@example.com`
- Check the name matches what you're using in the API call

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the API endpoints at http://localhost:8000/docs
- Check out `backend/examples/example_usage.py` for more examples
