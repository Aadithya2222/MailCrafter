# Architecture Overview

## Design Decisions

### 1. Modular Service-Based Architecture

**Decision**: Separate business logic into independent service classes.

**Rationale**:
- **Testability**: Each service can be tested independently
- **Maintainability**: Changes to one service don't affect others
- **Scalability**: Services can be replaced or upgraded independently
- **Separation of Concerns**: Clear boundaries between responsibilities

**Services**:
- `STTService`: Speech-to-text conversion (Whisper or stub)
- `IntentParser`: Extracts recipient names and email intent
- `GeminiService`: Professional email rewriting and subject generation
- `EmailService`: SMTP email sending
- `RecipientResolver`: Contact lookup and email resolution

### 2. Security-First Design

**Decision**: Never store email body content, only metadata.

**Rationale**:
- **Privacy**: Email content is sensitive and shouldn't be persisted
- **Compliance**: Reduces data protection and GDPR concerns
- **Trust**: Users can be confident their emails aren't being stored
- **Minimal Attack Surface**: Less data = less risk

**Implementation**:
- Email body is only in memory during processing
- Database stores only contact information (name, email)
- No logging of email content
- Environment variables for all secrets

### 3. Accessibility-Friendly Design

**Decision**: Voice-first interface with clear API responses.

**Rationale**:
- **Inclusivity**: Supports blind and visually impaired users
- **Efficiency**: Voice input is faster than typing for many users
- **Natural Interaction**: Speaking is more natural than writing

**Implementation**:
- Audio input via standard HTTP multipart upload
- Clear, structured JSON responses
- Error messages are descriptive and actionable
- No visual-only dependencies

### 4. Configuration Management

**Decision**: Use Pydantic Settings with `.env` file.

**Rationale**:
- **Security**: Secrets never in code
- **Flexibility**: Easy to change without code modifications
- **Type Safety**: Pydantic validates configuration at startup
- **Environment-Specific**: Different configs for dev/staging/prod

**Implementation**:
- `backend/config.py` uses `pydantic_settings.BaseSettings`
- `.env.example` provides template
- `.env` is gitignored
- All secrets loaded at startup

### 5. Error Handling Strategy

**Decision**: Comprehensive error handling with user-friendly messages.

**Rationale**:
- **User Experience**: Clear error messages help users fix issues
- **Debugging**: Detailed logging for developers
- **Security**: Don't expose sensitive information in errors

**Implementation**:
- Try-catch blocks in all service methods
- HTTPException with appropriate status codes
- Logging for debugging (without sensitive data)
- Graceful degradation (e.g., stub STT when Whisper unavailable)

### 6. Database Choice: SQLite

**Decision**: Use SQLite for contact storage.

**Rationale**:
- **Simplicity**: No separate database server needed
- **Portability**: Single file, easy to backup
- **Sufficient**: Contact storage doesn't need complex queries
- **Upgrade Path**: Easy to migrate to PostgreSQL if needed

**Implementation**:
- SQLite database at `backend/data/contacts.db`
- Auto-created on first use
- Indexed for fast lookups
- Contact management utility included

### 7. API Design: RESTful with Clear Endpoints

**Decision**: Separate endpoints for each major operation.

**Rationale**:
- **Flexibility**: Clients can use individual steps or complete flow
- **Debugging**: Easier to test and debug individual steps
- **Composability**: Frontend can build custom workflows

**Endpoints**:
- `POST /api/v1/audio/transcribe`: Speech-to-text
- `POST /api/v1/email/generate`: Generate email (Gemini)
- `POST /api/v1/email/send`: Send email (SMTP)
- `POST /api/v1/email/process-and-send`: Complete flow

### 8. Gemini Prompt Engineering

**Decision**: Carefully crafted prompts for email rewriting and subject generation.

**Rationale**:
- **Quality**: Better prompts = better output
- **Consistency**: Structured prompts ensure consistent results
- **Context**: Include recipient name and intent for better personalization

**Implementation**:
- Separate prompts for rewriting and subject generation
- Context-aware (includes recipient name, intent)
- Clear instructions for professional tone
- No subject line in body prompt (prevents duplication)

## Data Flow

```
1. Audio Upload
   ↓
2. STT Service (Whisper)
   ↓
3. Intent Parser (Extract recipient & intent)
   ↓
4. Gemini Service (Rewrite email + Generate subject)
   ↓
5. Recipient Resolver (Lookup email address)
   ↓
6. Email Service (Send via SMTP)
   ↓
7. Response (Success confirmation)
```

## Security Layers

1. **Input Validation**: File type, size, duration checks
2. **Authentication**: Gmail App Password (not main password)
3. **No Storage**: Email bodies never persisted
4. **Environment Secrets**: All keys in `.env` (gitignored)
5. **Error Sanitization**: No sensitive data in error messages
6. **CORS**: Configurable origins for frontend

## Scalability Considerations

### Current Design (Single Server)
- Suitable for: Personal use, small teams, prototypes
- Limitations: Single point of failure, no horizontal scaling

### Future Enhancements
- **Queue System**: Add Celery/Redis for async processing
- **Database**: Migrate to PostgreSQL for production
- **Caching**: Redis for frequently accessed contacts
- **Load Balancer**: Multiple FastAPI instances
- **CDN**: For static frontend assets

## Testing Strategy

### Unit Tests (Recommended)
- Test each service independently
- Mock external dependencies (Gemini API, SMTP)
- Test error handling paths

### Integration Tests (Recommended)
- Test complete flow with mock services
- Test database operations
- Test API endpoints

### Manual Testing
- Use Swagger UI at `/docs`
- Test with real audio files
- Verify email delivery

## Deployment Considerations

### Development
- Run locally with `python -m backend.main`
- Use `.env` for configuration
- SQLite database

### Production (Future)
- Use environment variables (not `.env` file)
- PostgreSQL database
- Gunicorn/Uvicorn with multiple workers
- Reverse proxy (Nginx)
- SSL/TLS certificates
- Rate limiting
- Monitoring and logging

## Technology Choices

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Framework | FastAPI | Fast, modern, auto-docs, async support |
| AI | Gemini API | Google's latest, competitive with GPT |
| STT | Whisper | Open-source, high quality, free |
| Email | SMTP (Gmail) | Universal, reliable, App Password security |
| Database | SQLite | Simple, sufficient for contacts |
| Config | Pydantic Settings | Type-safe, validated configuration |

## Future Enhancements

1. **Frontend**: React/Vue microphone UI
2. **OAuth**: Gmail OAuth instead of App Password
3. **Templates**: Pre-defined email templates
4. **Multi-language**: Support for non-English speech
5. **Voice Feedback**: Audio confirmation for accessibility
6. **Batch Processing**: Process multiple emails
7. **Analytics**: Track usage (without storing content)
8. **Webhooks**: Notify external systems on send
