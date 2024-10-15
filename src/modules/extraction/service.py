from fastapi import UploadFile, HTTPException, status
from src.modules.extraction.constants import ALLOWED_FILE_TYPES
from src.modules.extraction.dependencies import get_openai_client
import aiofiles
import tempfile
import os
import logging
import openai
from openai import OpenAI
import json

async def process_file(file: UploadFile):
    # Check if the file type is allowed
    if file.content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type.")

    # Save the uploaded file to a temporary location
    try:
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, file.filename)
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
    except Exception as e:
        logging.exception("Error saving file")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error saving file.")
    finally:
        # Ensure the file is closed
        file.file.close()

    # Initialize extracted_text variable
    extracted_text = ""

    try:
        # Determine the file type and extract text accordingly
        if file.content_type == 'application/pdf':
            # Extract text from PDF using PyPDF2
            import PyPDF2

            try:
                with open(file_path, 'rb') as pdf_file:
                    reader = PyPDF2.PdfReader(pdf_file)
                    for page_num in range(len(reader.pages)):
                        page = reader.pages[page_num]
                        extracted_text += page.extract_text()
            except Exception as e:
                logging.exception("Error extracting text from PDF")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error extracting text from PDF.")
        # Remove or comment out the image extraction part
        # elif file.content_type.startswith('image/'):
        #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Image extraction is temporarily disabled.")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type.")
    finally:
        # Clean up the temporary file
        os.remove(file_path)
        os.rmdir(temp_dir)

    # Assistant instructions to be included in the message
    assistant_instructions = """
    You'll be given the text extracted from invoice documents. Single document can also contain multiple invoices. I want you to give data for multiple invoices from the document and put it in the JSON structure as provided below. Do not alter the details of the invoice. Put them in the JSON format as it is written in the invoice.

    IT MIGHT HAPPEN THAT YOU WILL NOT FIND FIELDS AS IT IS IN THAT CASE YOU HAVE TO ANALYZE IT AND FILL THE REQUIRED INFORMATION OR ELSE LEAVE FIELD EMPTY

    The output of the models must be in JSON and in the following format where every tag is equated to the right value from the input text.

    REMEMBER @#$%^ IS A DELIMITER YOU HAVE TO WRAP JSON IN IT

    and the format should always be like the following structure -
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

    REMEMBER @#$%^ IS A DELIMITER YOU HAVE TO WRAP JSON IN IT

    You must give the output only in JSON

    TRY TO GIVE ACCURATE RESULT DON'T GIVE INCORRECT RESULTS
    """

    # Combine the instructions with the extracted text
    message_content = f"{assistant_instructions}\n\nHere is the extracted text from the invoice(s):\n\n{extracted_text}"

    # Initialize OpenAI client
    openai.api_key = get_openai_client().api_key
    client = OpenAI(api_key=openai.api_key)

    # Retrieve and update the assistant to adjust temperature
    try:
        assistant = client.beta.assistants.retrieve(
            assistant_id='asst_wSJ8XdHegSfFiMpT8y1eSy7R'
        )

        # Update the assistant's temperature to a lower value
        assistant = client.beta.assistants.update(
            assistant_id=assistant.id,
            temperature=0.3  # Adjust as needed
        )
    except Exception as e:
        logging.exception("Error retrieving or updating assistant")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error retrieving or updating assistant.")

    # Create a thread
    try:
        thread = client.beta.threads.create()
    except Exception as e:
        logging.exception("Error creating thread")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating thread.")

    # Send the message to the assistant
    try:
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=message_content
        )
    except Exception as e:
        logging.exception("Error adding message to thread")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error adding message to thread.")

    # Run the assistant
    try:
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id
        )
    except Exception as e:
        logging.exception("Error running assistant")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error running assistant.")

    # Wait for the run to complete
    import time
    start_time = time.time()
    timeout = 120  # seconds
    while run.status != 'completed':
        if time.time() - start_time > timeout:
            logging.error("Assistant run timed out.")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Assistant run timed out.")
        time.sleep(2)
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        if run.status == 'failed':
            logging.error("Assistant run failed.")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Assistant run failed.")

    # Retrieve the assistant's response
    try:
        assistant_messages = client.beta.threads.messages.list(
            thread_id=thread.id
        )

        # Find the assistant's message
        assistant_message = None
        for message in assistant_messages.data:
            if message.role == 'assistant':
                assistant_message = message
                break

        if assistant_message is None:
            logging.error("Assistant did not provide a response.")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Assistant did not provide a response.")

        # Extract the assistant's response
        assistant_response = ''.join(
            block.text.value for block in assistant_message.content if hasattr(block, 'text')
        )

        # Split the response by '@#$%^' and extract the JSON content
        try:
            parts = assistant_response.split('@#$%^')
            if len(parts) >= 3:
                json_content = parts[1]
            else:
                logging.error("Could not find JSON content between markers.")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not find JSON content between markers.")

            # Parse the JSON content
            assistant_response_data = json.loads(json_content.strip())
        except json.JSONDecodeError as e:
            logging.exception("Failed to parse assistant's response as JSON")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to parse assistant's response as JSON.")
        except Exception as e:
            logging.exception("Error processing assistant's response")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error processing assistant's response.")

    except Exception as e:
        logging.exception("Error retrieving assistant response")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error retrieving assistant response.")

    return assistant_response_data