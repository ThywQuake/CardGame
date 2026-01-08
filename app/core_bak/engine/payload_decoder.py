import json
from typing import Any, Dict


def decode_payload(payload: str) -> Dict[str, Any]:
    """
    Decodes a JSON-encoded string payload into a Python dictionary.

    Args:
        payload (str): The JSON-encoded string.
    Returns:
        Dict[str, Any]: The decoded payload as a dictionary.
    """
    try:
        decoded_data = json.loads(payload)
        if not isinstance(decoded_data, dict):
            raise ValueError("Decoded payload is not a dictionary.")
        return decoded_data
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON payload: {e}")
