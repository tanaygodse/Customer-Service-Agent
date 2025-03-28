from pydantic import BaseModel
import logging
from app.utils.LLM import LLMClient
from app.config import config


class ClassificationModel(BaseModel):
    classification: str
    confidence_score: float


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def classify_input_node(state: dict) -> dict:
    """
    Uses ChatGPT via an asynchronous LLM call to classify the customer message
    into one of three types and generate a confidence score, returning structured output.
    """
    message = state.get("message", "")
    product = state.get("product", "")

    if product not in config["products"]:
        logger.error("Invalid Product")
        return {
            "classification": "",
            "confidence_score": 0,
            "customer_id": state.get("customer_id"),
            "message": message,
            "product": state.get("product"),
        }

    prompt = (
        "You are an expert at customer service message classification. "
        "Based on the following customer message, determine whether the message is a "
        "'bug_report', 'feature_request', or 'general_inquiry'. Errors and bugs count towards bug_report, "
        "any requests for new features count as feature_request, and general comments or questions count towards general_inquiry. "
        "Also, provide a confidence score between 0 and 1 indicating your confidence in this classification. "
        "Return your answer as a JSON object with the keys 'classification' and 'confidence_score'.\n\n"
        f'Customer message: "{message}"'
    )

    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that classifies customer messages.",
        },
        {"role": "user", "content": prompt},
    ]
    llm_client = LLMClient()
    response = llm_client.parse(
        model=config["model"],
        messages=messages,
        response_format=ClassificationModel,
    )
    try:
        data = response.model_dump()
    except Exception as e:
        logger.error(e)
        data = {"classification": "general_inquiry", "confidence_score": 0}

    return {
        "classification": data.get("classification", "general_inquiry"),
        "confidence_score": data.get("confidence_score", 0),
        "customer_id": state.get("customer_id"),
        "message": message,
        "product": state.get("product"),
    }
