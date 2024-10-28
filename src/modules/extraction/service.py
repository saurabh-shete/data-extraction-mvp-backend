from openai import OpenAI
import aiofiles
import os
import logging
import json
import time
from fastapi import UploadFile, HTTPException, status
from PIL import Image
import pytesseract
import pdfplumber
from io import BytesIO
from src.modules.extraction.constants import ALLOWED_FILE_TYPES
from src.modules.extraction.dependencies import get_openai_client

# Define the base directory relative to the current file
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))

# Set the Tesseract binary path relative to BASE_DIR
pytesseract.pytesseract.tesseract_cmd = os.path.join(BASE_DIR, 'tesseract_bin/tesseract')

# Define tessdata directory path to pass directly in the config
tessdata_dir = os.path.join(BASE_DIR, 'tesseract_bin/tessdata')

async def process_file(file: UploadFile):
    # Check if the file type is allowed
    if file.content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type.")
    extracted_text = ""

    # Process PDF files
    if file.content_type == "application/pdf":
        try:
            # Read PDF content
            content = await file.read()
            with pdfplumber.open(BytesIO(content)) as pdf:
                # Extract text from each page
                for page in pdf.pages:
                    extracted_text += page.extract_text() + "\n"  # Concatenate text from all pages
        except Exception as e:
            logging.exception("Error processing PDF with pdfplumber")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error processing PDF with pdfplumber.")
    
    # Process Image files
    elif file.content_type in ['image/png', 'image/jpeg', 'image/jpg', 'image/gif']:
        try:
            # Read image content
            content = await file.read()
            image = Image.open(BytesIO(content))
            # Pass tessdata directory directly in the config parameter
            extracted_text = pytesseract.image_to_string(image, lang="eng", config=f'--tessdata-dir "{tessdata_dir}"')
        except Exception as e:
            logging.exception("Error processing image with Tesseract")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error processing image with Tesseract.")
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type.")

    print(extracted_text)
    # Combine the instructions with the extracted text for context
    message_content = f"Extracted Text: {extracted_text}"

    # Initialize OpenAI client with API key
    client = OpenAI(api_key=get_openai_client().api_key)

    # 2. Send the extracted text and instructions directly to OpenAI
    try:
        # Create a thread
        thread = client.beta.threads.create()

        # Send the prompt and extracted text to the assistant
        message = client.beta.threads.messages.create(thread_id=thread.id, role="user", content=message_content)

        # Run the assistant
        for attempt in range(3):
            try:
                run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id='asst_wSJ8XdHegSfFiMpT8y1eSy7R')  # Replace with your assistant ID
                break
            except Exception as e:
                logging.error(f"Error running assistant attempt {attempt + 1}: {str(e)}")
                time.sleep(2)
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="OpenAI request failed after retries.")

        # Wait for the run to complete with timeout logic
        start_time = time.time()
        timeout = 120  # seconds
        while run.status != 'completed':
            if time.time() - start_time > timeout:
                logging.error("Assistant run timed out.")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Assistant run timed out.")
            time.sleep(2)
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            if run.status == 'failed':
                logging.error("Assistant run failed.")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Assistant run failed.")

    except Exception as e:
        logging.exception("Error running assistant")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error running assistant.")

    # 3. Retrieve the assistant's response
    try:
        assistant_messages = client.beta.threads.messages.list(thread_id=thread.id)
        assistant_message = next((msg for msg in assistant_messages.data if msg.role == "assistant"), None)

        if assistant_message is None:
            logging.error("Assistant did not provide a response.")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Assistant did not provide a response.")

        # Extract and parse the assistant's JSON response
        assistant_response = ''.join(block.text.value for block in assistant_message.content if hasattr(block, 'text'))
        parts = assistant_response.split('@#$%^')

        if len(parts) >= 3:
            # JSON content found between markers
            json_content = parts[1]
            assistant_response_data = json.loads(json_content.strip())
        else:
            # No JSON content found between markers
            logging.error(f"Invalid assistant response format: {assistant_response}")
            return {
                "error": "Invalid assistant response format: Couldn't find any relevant information in the document. Please ensure the document contains the necessary details or try uploading a different document"
            }

    except json.JSONDecodeError as e:
        logging.exception("Failed to parse assistant's response as JSON")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to parse assistant's response as JSON.")
    except Exception as e:
        logging.exception("Error processing assistant's response")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error processing assistant's response.")

    return assistant_response_data
