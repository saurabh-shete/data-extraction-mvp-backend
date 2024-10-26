from openai import OpenAI
import aiofiles
import os
import logging
import json
import time
from fastapi import UploadFile, HTTPException, status
from src.modules.extraction.constants import ALLOWED_FILE_TYPES
from src.modules.extraction.dependencies import get_openai_client

async def process_file(file: UploadFile):
    # Check if the file type is allowed
    if file.content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type.")

    # Initialize OpenAI client with API key
    client = OpenAI(api_key=get_openai_client().api_key)

    # 1. Upload the file to OpenAI
    try:
        async with aiofiles.tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name
            content = await file.read()
            await temp_file.write(content)
        
        with open(temp_file_path, "rb") as temp_file:
            file_response = client.files.create(
                file=temp_file,
                purpose="assistants"
            )
            # Access the file ID as an attribute, not a dictionary key
            file_id = file_response.id

    except Exception as e:
        logging.exception("Error uploading file to OpenAI")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error uploading file to OpenAI.")

    finally:
        # Delete the local temporary file
        os.remove(temp_file_path)


    # Assistant instructions to be included in the message
    assistant_instructions = """
    You'll be given the text extracted from invoice documents. A single document may contain multiple invoices. I want you to extract data for multiple invoices from the document in the JSON format provided below. Do not alter invoice details, and enter them as they appear in the invoice.

    If specific fields are missing, analyze and leave them empty if data is not available.

    Wrap the JSON output in @#$%^ delimiters as shown below:
    @#$%^{
        "number_of_invoices": "",
        "invoices": [
            {
                "dealer_details": {
                    "dealer_name": "",
                    "dealer_gst_no": ""
                },
                "buyer_details": {
                    "buyer_name": "",
                    "buyer_address": "",
                    "buyer_gst_no": ""
                },
                "purchase_order_details": {
                    "po_no": "",
                    "po_date": ""
                },
                "invoice_details": {
                    "number_of_pages":"",
                    "date_of_invoice": "",
                    "invoice_no": "",
                    "irn_no": ""
                },
                "eway_bill_details": {
                    "eway_bill_no": "",
                    "eway_bill_date": ""
                },
                "item_details": [
                    {
                        "item_code": "",
                        "quantity": ""
                    }
                ]
            }
        ]
    }@#$%^
    ONLY respond in JSON format.
    """

    # Combine the instructions with the extracted file ID for context
    message_content = f"{assistant_instructions}\n\nFile ID: {file_id}"

    # 2. Initialize the assistant and send the extraction prompt
    try:
        # Retrieve and configure the assistant
        assistant = client.beta.assistants.retrieve(assistant_id='asst_wSJ8XdHegSfFiMpT8y1eSy7R')
        assistant = client.beta.assistants.update(
            assistant_id=assistant.id, 
            temperature=0.3,
            tools=[{"type": "code_interpreter"}],
            tool_resources={
                "code_interpreter": {
                "file_ids": [file_id]
                }
            }
        )

        # Create a thread
        thread = client.beta.threads.create()

        # Send the prompt and file reference to the assistant
        message = client.beta.threads.messages.create(thread_id=thread.id, role="user", content=message_content)

        # Run the assistant
        for attempt in range(3):
            try:
                run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant.id)
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

    # 4. Delete the file from OpenAI storage
    try:
        client.files.delete(file_id)
    except Exception as e:
        logging.exception("Error deleting file from OpenAI")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting file from OpenAI.")

    return assistant_response_data
