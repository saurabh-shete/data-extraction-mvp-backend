from fastapi.responses import JSONResponse
import logging

# Success response
def OK(status_code: int, data: dict):
    """
    Sends a successful response.
    :param status_code: HTTP status code.
    :param data: The data to include in the response.
    :return: A JSONResponse object with the provided data and status code.
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "success": True,
            "result":{**data}
        }
    )

# Error response
def throw_error(status_code: int, error_message: str):
    """
    Throws an error response with a specific status code and message.
    :param status_code: HTTP status code.
    :param error_message: The error message.
    :return: A JSONResponse object with the error message and status code.
    """
    logging.error(f"Error()- {error_message}")
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": error_message,
            "code": status_code
        }
    )