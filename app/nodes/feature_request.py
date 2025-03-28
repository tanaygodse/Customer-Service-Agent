from pydantic import BaseModel
import logging
from app.config import config
from app.utils.LLM import LLMClient

# Global counter for Feature Requests.
FR_COUNTER = 1


class FeatureRequestModel(BaseModel):
    title: str
    description: str
    user_story: str
    business_value: str
    affected_components: list[str]
    missing_fields: list[str]


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def feature_request_extraction_node(state: dict) -> dict:
    """
    Uses ChatGPT via a synchronous LLM call (inside an async function) to extract feature request details.
    Expected fields: 'title', 'description', 'user_story', and 'affected_components' (list).
    If a field cannot be extracted from the customer message, return "UNKNOWN_VALUE" for that field.
    If any required fields are missing, include a 'missing_fields' list in the response.
    Returns the answer as a JSON object matching the FeatureRequestModel.
    Then, constructs a product requirement ticket with a global counter and default values:
      - business_value: "TBD"
      - complexity_estimate: "TBD"
      - status: "TBD"
    """
    message = state.get("message", "")

    product = state.get("product", "")

    if product not in config["products"]:
        logger.error("Invalid Product")
        return {"customer_response": "Invalid Product Name", "response_data": {}}

    components_list = config["products"][product]["component_team_mapping"].keys()
    description = config["products"][product]["description"]

    prompt = (
        "You are an expert at extracting feature request details from customer messages. "
        "Extract the following fields from the message: 'title', 'description', 'user_story', and 'affected_components' (as a list). "
        "Come up with a relevant title based on the message provided by the user. "
        "For 'affected_components', choose the most appropriate ones from the following list: "
        f"{components_list}. "
        "The 'business_value' should be set to High/Medium/Low based on the feature request with respect to the description for the application provided"
        f"Description for the application: {description}."
        "Strictly fill in the only the details that can be inferred from the customer message other than this."
        "If a field cannot be determined from the message, use the value 'UNKNOWN_VALUE' for that field. "
        "Do not hallucinate or make assumptions."
        "If any field is missing, include a 'missing_fields' list in your JSON output containing the names of the missing fields. "
        "Return your answer as a JSON object with these keys.\n\n"
        f'Customer message: "{message}"'
    )

    messages = [
        {
            "role": "system",
            "content": "You are an expert at extracting structured feature request details.",
        },
        {"role": "user", "content": prompt},
    ]

    llm_client = LLMClient()
    response = llm_client.parse(
        model=config["model"],
        messages=messages,
        response_format=FeatureRequestModel,
    )
    try:
        data = response.model_dump()
    except Exception as e:
        logger.error(e)
        data = {
            "title": "UNKNOWN_VALUE",
            "description": "UNKNOWN_VALUE",
            "user_story": "UNKNOWN_VALUE",
            "affected_components": ["UNKNOWN_VALUE"],
            "missing_fields": [
                "title",
                "description",
                "user_story",
                "affected_components",
            ],
        }

    global FR_COUNTER
    product_requirement = {
        "id": f"FR-{FR_COUNTER}",
        "title": data.get("title", "UNKNOWN_VALUE"),
        "description": data.get("description", "UNKNOWN_VALUE"),
        "user_story": data.get("user_story", "UNKNOWN_VALUE"),
        "business_value": data.get("business_value", "Medium"),
        "complexity_estimate": "Medium",
        "affected_components": data.get("affected_components", []),
        "status": "Under Review",
    }
    FR_COUNTER += 1

    customer_response = f"Thank you for your feature request. Your request has been recorded with ID {product_requirement['id']}."
    return {
        "customer_response": customer_response,
        "response_data": {"product_requirement": product_requirement},
    }
