import json
import datetime
import math
from typing import Any, Dict
from supabase_client import supabase  # Ensure this imports the initialized Supabase client
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def replace_nan(obj: Any) -> Any:
    """Recursively replace NaN values in a nested structure with None."""
    if isinstance(obj, dict):
        return {k: replace_nan(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_nan(item) for item in obj]
    elif isinstance(obj, float):
        return None if math.isnan(obj) else obj
    else:
        return obj


# supascript.py

import datetime
import math
import logging
from typing import Any, Dict
from supabase_client import supabase  # Ensure this imports the initialized Supabase client

# Configure logging
logger = logging.getLogger(__name__)

def replace_nan(obj: Any) -> Any:
    """Recursively replace NaN values in a nested structure with None."""
    if isinstance(obj, dict):
        return {k: replace_nan(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_nan(item) for item in obj]
    elif isinstance(obj, float):
        return None if math.isnan(obj) else obj
    else:
        return obj

def push_sustainability_data(payload: Dict[str, Any], user_id: str):
    """
    Pushes sustainability data to Supabase.

    Args:
        payload (dict): The data payload to insert into Supabase.
        user_id (str): The ID of the user pushing the data.
    """
    try:
        logger.info(f"Received payload: {payload}")

        # Extract num_shipments from payload
        num_shipments = payload['batch_analysis']['num_shipments_analyzed']
        if num_shipments is None:
            num_shipments = len(payload.get('results', []))
            logger.warning("num_shipments_analyzed not found. Using length of results.")

        logger.info(f"Extracted num_shipments: {num_shipments}")

        # Validate that num_shipments is an integer
        if not isinstance(num_shipments, int):
            raise ValueError(f"'num_shipments_analyzed' must be an integer, got {type(num_shipments)}")

        # Structure the payload to match Supabase table schema
        insertion_payload = {
            "user_id": user_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "num_shipments": num_shipments,
            "data": payload['batch_analysis']
        }

        # Replace NaN values with None
        safe_insertion_payload = replace_nan(insertion_payload)
        logger.info(f"Safe Insertion Payload: {safe_insertion_payload}")

        # Insert data into Supabase
        response = supabase.table("sustainability_analytics").insert(safe_insertion_payload).execute()


        # Handle response based on status code
        if not response.data:
            logger.error(f"Failed to push data. Error: {response.status_code} - {response.text}")
            raise Exception(f"Failed to push data. Error: {response.status_code} - {response.text}")
        else:
            logger.info("Data pushed to Supabase successfully.")

    except Exception as e:
        logger.exception("Error pushing sustainability data:")
        raise e