# Report Card Validator

A system for validating and comparing student report card PDFs using Google ADK Agents to check for consistency, correctness, and identity matching.

## Project Overview

The Report Card Validator analyzes pairs of PDF report cards to verify their authenticity and consistency. It performs automated validation checks including:

- Verifying both documents are legitimate report cards
- Checking if the documents belong to the same student
- Validating pagination correctness across pages
- Ensuring content consistency within each document
- Detecting duplicate documents via file hashing

## Setup

1. **Environment Variables**: Create a `.env` file with your Google API key:
   ```
   GOOGLE_GENAI_USE_VERTEXAI=FALSE
   GOOGLE_API_KEY=your_api_key_here
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   # or if using pyproject.toml:
   pip install -e .
   ```

## Usage

Run the validation tests:

```bash
python main.py
```

This will process test cases comparing different report card PDFs and output the validation results in JSON format.

## API Key Configuration

The application automatically loads the Google API key from the `.env` file using python-dotenv. The API key is used to authenticate with Google's Gemini AI model through the Google ADK (Agent Development Kit).

## Dependencies

- `google-adk`: For AI-powered document analysis using Google Gemini
- `python-dotenv`: For loading environment variables from .env file
      "pagination_correct": true|false,
      "content_consistent": true|false,
      "errors": "Error message or null"
    },
    "file_2_validation": {
      "is_report_card": true|false,
      "pagination_correct": true|false,
      "content_consistent": true|false,
      "errors": "Error message or null"
    }
  }
}
```

## Dependencies

- `pypdf`: For extracting text from PDF files
- `google.adk.agents`: For the LLM-based implementation (only needed for the src version)

## Project Status

This project provides two complete implementations for report card validation:
1. A direct Python approach for deterministic validation
2. An AI-assisted approach for more nuanced content analysis