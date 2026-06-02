# Voice Digital Twin Implementation Guide

## Overview

This guide documents the Voice Digital Twin feature for OSSify (Step 9). The feature allows users to ask questions about a contributor's work using voice input, which is transcribed using Groq Whisper and answered using the existing contributor-scoped RAG pipeline.

**Key characteristics:**
- Audio input → Groq Whisper transcription → Existing RAG pipeline → JSON response
- No new retrieval or RAG logic introduced
- Contributor-scoped isolation (only retrieves documents from specified contributor)
- Supports MP3, WAV, OGG, FLAC, and M4A audio formats

---

## Files Modified

### 1. **backend/app/services/voice_chat_service.py** (NEW)
- **Purpose:** Voice transcription and RAG orchestration service
- **Key functions:**
  - `transcribe_audio_with_groq()` - Transcribes audio using Groq Whisper API
  - `voice_chat_with_contributor()` - Main orchestration function

### 2. **backend/app/api/v1/endpoints/experts.py** (MODIFIED)
- **Added imports:**
  - `UploadFile, File` from FastAPI
  - `voice_chat_with_contributor` from voice_chat_service
- **Added Pydantic schema:**
  - `ContributorVoiceChatResponse` - Response model for voice chat endpoint
- **Added endpoint:**
  - `POST /contributors/{contributor_id}/voice-chat` - Voice chat endpoint

### 3. **backend/requirements.txt** (MODIFIED)
- **Added dependencies:**
  - `groq>=0.4.1` - Groq SDK for Whisper and LLM APIs
  - `python-multipart>=0.0.5` - Multipart form data parsing

---

## Endpoint Specification

### POST `/contributors/{contributor_id}/voice-chat`

**Request:**
```
Method: POST
Content-Type: multipart/form-data

Parameters:
  - contributor_id (path, integer, required): Local PostgreSQL contributor ID
  - audio_file (form, file, required): Audio file (MP3, WAV, OGG, FLAC, M4A)
  - top_k (query, integer, optional): Number of evidence documents (default=5, max=15)
```

**Response:** (200 OK)
```json
{
  "contributor_id": 1,
  "username": "john_doe",
  "transcript": "What has this contributor worked on recently?",
  "answer": "Based on the documents, John has been working on...",
  "evidence": [
    {
      "document_type": "commit",
      "content_snippet": "Fixed authentication bug in login flow",
      "score": 0.8523,
      "commit_sha": "abc123def456",
      "pr_number": null,
      "issue_number": null
    }
  ],
  "grounding_status": "contributor_scoped",
  "document_count": 3
}
```

**Error Responses:**
- **400 Bad Request:** Missing/invalid audio file, empty transcription, invalid contributor
- **404 Not Found:** Contributor not found
- **413 Payload Too Large:** Audio file exceeds 25 MB limit
- **500 Internal Server Error:** Transcription or RAG pipeline failure

---

## Installation & Setup

### Step 1: Update Dependencies

Install the new required packages:

```bash
cd backend
pip install -r requirements.txt
```

Or install just the new dependencies:

```bash
pip install "groq>=0.4.1" "python-multipart>=0.0.5"
```

### Step 2: Verify GROQ_API_KEY

Ensure your environment has the `GROQ_API_KEY` set:

```bash
# Check if it's already set
echo $GROQ_API_KEY

# Or add to .env file in project root
echo "GROQ_API_KEY=your_groq_api_key_here" >> .env

# Load environment variables
source .env  # On Linux/macOS
# or on Windows PowerShell:
# Get-Content .env | ForEach-Object { if ($_) { $name, $value = $_ -split '=', 2; [Environment]::SetEnvironmentVariable($name, $value) } }
```

### Step 3: Start the Backend Server

```bash
# From the project root
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

---

## Testing the Endpoint

### Method 1: Using curl (Command Line)

**Test with a sample audio file:**

```bash
# Download a sample audio file or record one yourself
# For testing, you can use any MP3/WAV file

curl -X POST "http://localhost:8000/contributors/1/voice-chat" \
  -F "audio_file=@path/to/audio.mp3" \
  -F "top_k=5"
```

**Expected output:**
```json
{
  "contributor_id": 1,
  "username": "john_doe",
  "transcript": "What have you worked on",
  "answer": "Based on my contributions...",
  "evidence": [...],
  "grounding_status": "contributor_scoped",
  "document_count": 3
}
```

### Method 2: Using Swagger/FastAPI Docs

1. Start the backend server (see above)
2. Open browser: http://localhost:8000/docs
3. Scroll down to find: `POST /contributors/{contributor_id}/voice-chat`
4. Click "Try it out"
5. Enter:
   - `contributor_id`: 1 (or any valid ID)
   - `audio_file`: Click "Select file" and choose your audio
   - `top_k`: 5 (optional)
6. Click "Execute"

### Method 3: Using Python Requests

```python
import requests

# Prepare the file
with open("audio.mp3", "rb") as f:
    files = {"audio_file": f}
    data = {"top_k": 5}
    
    response = requests.post(
        "http://localhost:8000/contributors/1/voice-chat",
        files=files,
        data=data
    )
    
    print(response.json())
```

### Method 4: Using JavaScript Fetch API

```javascript
// From a web frontend
const formData = new FormData();
formData.append("audio_file", audioFileInput.files[0]);
formData.append("top_k", 5);

const response = await fetch(
  "http://localhost:8000/contributors/1/voice-chat",
  {
    method: "POST",
    body: formData
  }
);

const result = await response.json();
console.log(result);
```

---

## Creating Test Audio Files

### Quick Test with ffmpeg

If you have ffmpeg installed, create a simple test audio:

```bash
# Generate a 3-second sine wave audio at 440Hz
ffmpeg -f lavfi -i sine=f=440:d=3 -q:a 9 -acodec libmp3lame test_audio.mp3

# Or use a text-to-speech approach (requires additional tools):
espeak "What is the contributor working on" -w test_audio.wav
```

### Using Online Tools

1. Visit https://www.ttsmp3.com/ or similar
2. Enter text: "Tell me about the authentication changes in the last commit"
3. Download as MP3
4. Use the downloaded file for testing

### Using Your Own Voice

Use any audio recorder (e.g., Audacity, Voice Memos, QuickTime) to record a 10-15 second audio clip asking a question about a contributor's work.

---

## Error Handling

### Common Errors & Solutions

**Error: `GROQ_API_KEY not found`**
```
Status: 500
Detail: "GROQ_API_KEY environment variable is not set"
```
**Solution:** Set the GROQ_API_KEY environment variable (see Setup Step 2)

**Error: `Audio file too large`**
```
Status: 413
Detail: "Audio file too large (max 25 MB)"
```
**Solution:** Use a smaller audio file or compress it first

**Error: `Empty transcription`**
```
Status: 400
Detail: "Audio transcription resulted in empty text"
```
**Solution:** 
- Ensure audio is clear and audible
- Use a different audio file
- Check that the audio format is supported

**Error: `Contributor not found`**
```
Status: 400
Detail: "Contributor with ID 999 not found"
```
**Solution:** Use a valid contributor ID from your PostgreSQL database

**Error: `Missing audio_file in request`**
```
Status: 400
Detail: "Missing audio_file in request"
```
**Solution:** Ensure the form field is named `audio_file` and is properly attached

---

## Response Field Reference

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `contributor_id` | integer | PostgreSQL contributor ID |
| `username` | string | Contributor's username |
| `transcript` | string | Transcribed text from audio input |
| `answer` | string | LLM-generated response based on contributor's documents |
| `evidence` | array | List of matched documents grounding the answer |
| `grounding_status` | string | "contributor_scoped" or "no_matches" |
| `document_count` | integer | Number of retrieved documents |

### Evidence Document Structure

| Field | Type | Description |
|-------|------|-------------|
| `document_type` | string | "commit", "pr", or "issue" |
| `content_snippet` | string | First 400 characters of document content |
| `score` | float | Semantic relevance score (0.0-1.0) |
| `commit_sha` | string/null | Commit SHA if document type is "commit" |
| `pr_number` | integer/null | PR number if document type is "pr" |
| `issue_number` | integer/null | Issue number if document type is "issue" |

---

## Architecture & Design Decisions

### No New RAG Logic

The implementation **reuses** the existing `answer_for_contributor()` function from `expert_retrieval_service.py`. This ensures:
- Consistency with the text chat endpoint
- No duplicated retrieval logic
- Same evidence format and grounding guarantees
- Same contributor-scoped isolation

### Pipeline Flow

```
1. Audio File Upload
        ↓
2. Validate file (size, format)
        ↓
3. Groq Whisper Transcription (whisper-large-v3)
        ↓
4. Extract transcript text
        ↓
5. Validate transcript (non-empty)
        ↓
6. Call answer_for_contributor(contributor_id, transcript, top_k)
        ↓
7. Reuse RAG pipeline (Qdrant search, evidence extraction)
        ↓
8. Groq LLM generates answer
        ↓
9. Return response with transcript + answer + evidence
```

### Contributor-Scoped Isolation

All retrieval is filtered to the specified contributor via Qdrant metadata filtering:
```python
retriever.search_by_contributor(
    query=transcript,
    contributor_id=contributor_id,
    top_k=top_k
)
```

This guarantees:
- Only documents from the specified contributor are retrieved
- No cross-contamination with other contributors' data
- Consistent with the existing `/contributors/{id}/chat` endpoint

### Error Handling Strategy

**Layered error handling:**

1. **File Validation:**
   - Missing audio_file → 400
   - File too large → 413

2. **Transcription:**
   - GROQ_API_KEY missing → Caught and raised as 500
   - Groq API failure → 500 with error detail
   - Empty transcript → 400

3. **RAG Pipeline:**
   - Contributor not found → 400 (from service)
   - Qdrant failure → 500
   - LLM generation failure → Falls back to "Error generating answer"

---

## Performance & Limits

| Limit | Value | Notes |
|-------|-------|-------|
| Max audio file size | 25 MB | Groq's file upload limit is reasonable |
| Supported formats | MP3, WAV, OGG, FLAC, M4A | Groq Whisper supports all major formats |
| Max top_k | 15 | Same as text chat endpoint |
| Transcription model | whisper-large-v3 | Highest accuracy variant |
| Typical latency | 5-30 seconds | Depends on audio length and Groq queue |

---

## Next Steps (Phase 2)

The current implementation (Phase 1) focuses on:
- Audio → Transcription → Existing RAG → Response

**Phase 2 (not yet implemented) could add:**
- Text-to-speech for answers (e.g., ElevenLabs API)
- Real-time streaming transcription
- Audio response format preferences
- Voice biometric verification

---

## References & Useful Links

- [Groq Whisper API Docs](https://console.groq.com/docs/speech-text)
- [Groq Chat Completions API Docs](https://console.groq.com/docs/chat-completions)
- [FastAPI File Upload Docs](https://fastapi.tiangolo.com/tutorial/request-files/)
- [Pydantic File Upload](https://fastapi.tiangolo.com/tutorial/request-files/#uploading-files)

---

## Quick Verification Checklist

Before deployment, verify:

- [ ] `backend/requirements.txt` includes `groq>=0.4.1` and `python-multipart>=0.0.5`
- [ ] `backend/app/services/voice_chat_service.py` exists and has no syntax errors
- [ ] `backend/app/api/v1/endpoints/experts.py` imports new service
- [ ] `ContributorVoiceChatResponse` schema is defined
- [ ] `POST /contributors/{contributor_id}/voice-chat` endpoint is defined
- [ ] GROQ_API_KEY is set in environment
- [ ] Backend server starts without errors
- [ ] Swagger docs at `/docs` shows new endpoint
- [ ] Endpoint accepts file upload and returns expected response

---

## Support & Troubleshooting

If you encounter issues:

1. **Check logs:** Review console output from FastAPI server for detailed error messages
2. **Validate audio:** Ensure audio file is valid (test with a tool like ffmpeg)
3. **Check GROQ_API_KEY:** Verify it's set and valid with Groq's website
4. **Test with text first:** Try `/contributors/{id}/chat` endpoint to verify RAG pipeline works
5. **Recreate environment:** Run `pip install -r backend/requirements.txt` again

For Groq-specific issues, consult [Groq's documentation](https://console.groq.com/docs) or contact Groq support.
