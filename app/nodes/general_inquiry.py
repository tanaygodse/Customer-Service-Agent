from pydantic import BaseModel
import logging
from app.config import config
from app.utils.LLM import LLMClient


class GeneralInquiryModel(BaseModel):
    inquiry_category: str
    requires_human_review: bool


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def general_inquiry_extraction_node(state: dict) -> dict:
    """
    Uses ChatGPT via a synchronous LLM call (inside an async function) to extract general inquiry details.
    Expected output: a JSON object with the key 'inquiry_category' (which should be one of:
    'Account Management', 'Billing', 'Usage Question', or 'Other').
    Then, using a pre-defined resource dictionary, the function determines the suggested resources and whether
    human review is required.
    """
    message = state.get("message", "")

    product = state.get("product", "")

    if product not in config["products"]:
        logger.error("Invalid Product")
        return {"customer_response": "Invalid Product Name", "response_data": {}}

    resource_dict = config["products"][product]["general_inquiry"]["resource_dict"]
    inquiry_categories = resource_dict.keys()

    prompt = (
        "You are an expert at determining inquiry categories from customer messages. "
        "Based on the following customer message, determine the inquiry category. "
        f"The 'inquiry_category' should be one of the following: {inquiry_categories}"
        "The 'requires_human_review' should be marked as True if the category cannot be identified or if the user was"
        " not able to solve their problem using the resources provided by the system"
        "Strictly fill in the only the details that can be inferred from the customer message other than this."
        "If a field cannot be determined from the message, use the value 'UNKNOWN_VALUE' for that field. "
        "Do not hallucinate or make assumptions."
        "Return your answer as a JSON object with the keys 'inquiry_category' and 'requires_human_review'.\n\n"
        f'Customer message: "{message}"'
    )

    messages = [
        {
            "role": "system",
            "content": "You are an expert at extracting structured general inquiry details.",
        },
        {"role": "user", "content": prompt},
    ]

    llm_client = LLMClient()
    response = llm_client.parse(
        model=config["model"],
        messages=messages,
        response_format=GeneralInquiryModel,
    )
    try:
        data = response.model_dump()
    except Exception as e:
        logger.error(e)
        data = {"inquiry_category": "Other"}

    # Use the extracted inquiry_category and include the resource dictionary logic.
    inquiry_category = data.get("inquiry_category", "Other")

    suggested_resources = resource_dict.get(inquiry_category, [])
    requires_human_review = data.get("requires_human_review", False)
    if inquiry_category != "Other":
        customer_response = "Thank you for your inquiry. Please refer to the following resources or wait for further assistance."
    else:
        customer_response = "Thank you for your inquiry. Your inquiry has been noted, you will be contacted for further assistance."

    response_data = {
        "inquiry_category": inquiry_category,
        "requires_human_review": requires_human_review,
        "suggested_resources": suggested_resources,
    }

    return {"customer_response": customer_response, "response_data": response_data}
