import os
import json
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService
from google.genai import types

# Load environment variables
load_dotenv()

def validate_environment():
    """Validate that required environment variables are set."""
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables. Please check your .env file.")
    
    # Set the API key for google.genai if needed
    os.environ['GOOGLE_API_KEY'] = api_key
    return api_key

async def run_validation(file1_path: str, file2_path: str) -> dict:
    """
    Run the validation using Google ADK with artifacts.
    """
    # Validate environment variables
    validate_environment()
    
    # Create artifact service and session service
    artifact_service = InMemoryArtifactService()
    session_service = InMemorySessionService()
    
    # Create agent
    agent_instruction = """
You are a highly specialized AI agent tasked with validating and comparing two student report card PDF files. Your ONLY job is to produce a single, precise JSON object summarizing your findings based on the file artifacts provided.

**CRITICAL INSTRUCTIONS - FOLLOW THESE EXACTLY:**

1. **Analyze Artifacts**: You will receive two PDF files as artifacts. You MUST extract their actual file names and their text content to perform your analysis.
2. **Strict JSON Output**: Your entire response MUST be a single JSON object. Do not add any introductory text, explanations, or markdown formatting around the JSON.
3. **Follow Logic Precisely**: Apply the validation logic exactly as described below.

**VALIDATION LOGIC:**

- **`file_1` & `file_2`**: Use the actual file names of the artifacts.
- **`student_identity_match`**: Extract 'Student Name' and 'Roll Number' from both files. true only if BOTH name and roll number are identical. Otherwise false.
- **`files_are_duplicates`**: true only if the content of both files is exactly the same.
- **`is_report_card`**: true if the document contains "Report Card," "Progress Report," or "Scorecard."
- **`pagination_correct`**: true if page numbers are sequential and correct (e.g., "Page 1 of 2", "Page 2 of 2"). false for any errors.
- **`content_consistent`**: true if all pages in a single file belong to the same student. Check for student name mismatches across pages - if you find a different student name on any page, this should be false.
- **`errors`**: If a check fails, provide a specific error message explaining the issue. If all pass, this MUST be null.

**CRITICAL:** All boolean values (student_identity_match, files_are_duplicates, is_report_card, pagination_correct, content_consistent) MUST be actual boolean values (true/false), NOT strings ("true"/"false").

**ERROR MESSAGE FORMATS:**
- For content inconsistency with different student: "Anomaly Detected: Page X contains data (Student Name: [Different Student Name]) inconsistent with the rest of the document."
- For pagination errors: "Pagination Error: Page sequence is incorrect. Found issue at Page X."
- For non-report cards: "Validation Error: Document is not a report card."


**JSON OUTPUT STRUCTURE:**
{
  "file_1": "<actual name of the first file>",
  "file_2": "<actual name of the second file>",
  "validation_summary": {
    "student_identity_match": "<boolean>",
    "files_are_duplicates": "<boolean>",
    "file_1_validation": {
      "is_report_card": "<boolean>",
      "pagination_correct": "<boolean>",
      "content_consistent": "<boolean>",
      "errors": "<string|null>"
    },
    "file_2_validation": {
      "is_report_card": "<boolean>",
      "pagination_correct": "<boolean>",
      "content_consistent": "<boolean>",
      "errors": "<string|null>"
    }
  }
}
"""

    root_agent = Agent(
        name="report_card_validator",
        model="gemini-2.5-flash",
        description="An AI agent that validates and compares two student report card documents by processing file artifacts.",
        instruction=agent_instruction,
        tools=[],
    )
    
    # Create runner with artifact service
    runner = Runner(
        agent=root_agent,
        app_name="report_card_validator",
        session_service=session_service,
        artifact_service=artifact_service
    )
    
    # Create session
    session = await session_service.create_session(
        app_name="report_card_validator",
        user_id="user_1",
        session_id="session_1"
    )
    
    # Read PDF files and create artifacts
    with open(file1_path, 'rb') as f:
        file1_bytes = f.read()
    with open(file2_path, 'rb') as f:
        file2_bytes = f.read()
    
    file1_artifact = types.Part.from_bytes(
        data=file1_bytes,
        mime_type="application/pdf"
    )
    file2_artifact = types.Part.from_bytes(
        data=file2_bytes,
        mime_type="application/pdf"
    )
    
    # Create message content with artifacts
    content_parts = [
        types.Part(text=f"Please validate and compare these two PDF report cards: {os.path.basename(file1_path)} and {os.path.basename(file2_path)}"),
        file1_artifact,
        file2_artifact
    ]
    
    content = types.Content(role='user', parts=content_parts)
    
    # Run the agent
    final_response = None
    async for event in runner.run_async(
        user_id="user_1",
        session_id="session_1",
        new_message=content
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                final_response = event.content.parts[0].text
            break
    
    # Parse the JSON response
    try:
        if final_response:
            # Clean up the response to extract JSON
            response_text = final_response.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            return json.loads(response_text.strip())
        else:
            return {"error": "No response received from agent"}
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse JSON response: {e}", "raw_response": final_response}
