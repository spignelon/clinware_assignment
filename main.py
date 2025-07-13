import asyncio
import json
import os
from dotenv import load_dotenv
from report_card_validator.agent import run_validation

# Load environment variables from .env file
load_dotenv()


async def run_test_case(file_1, file_2):
    """
    Runs a test case using the Google ADK agent with artifacts.
    """
    print(
        "--- Running test case for"
        f" {os.path.basename(file_1)} and {os.path.basename(file_2)} ---"
    )
    
    # Convert relative paths to absolute paths
    file_1_abs = os.path.abspath(file_1)
    file_2_abs = os.path.abspath(file_2)
    
    validation_result = await run_validation(file_1_abs, file_2_abs)
    print(json.dumps(validation_result, indent=2))


async def main():
    """Runs all test cases."""
    test_cases = [
        (
            "report_cards/Ananya Sharma - 1.pdf",
            "report_cards/Ananya Sharma - 2.pdf",
        ),
        (
            "report_cards/Ananya Sharma - 1.pdf",
            "report_cards/Ananya Sharma - 3.pdf",
        ),
        ("report_cards/Ananya Sharma - 1.pdf", "report_cards/Rohan Verma.pdf"),
        (
            "report_cards/Ananya Sharma - 1.pdf",
            "report_cards/Ananya Sharma - 1.pdf",
        ),
    ]

    for file_1, file_2 in test_cases:
        await run_test_case(file_1, file_2)
        print("-" * 50)


if __name__ == "__main__":
    asyncio.run(main())
