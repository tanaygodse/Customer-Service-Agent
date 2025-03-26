from pydantic import BaseModel
import logging
from app.config import config
from app.utils.LLM import LLMClient

# Global counter for bug IDs.
BUG_COUNTER = 1


class BugReportModel(BaseModel):
    title: str
    reproduction_steps: list[str]
    affected_components: list[str]


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def bug_report_extraction_node(state: dict) -> dict:
    """
    Uses ChatGPT via a synchronous LLM call (inside an async function) to extract bug report details.
    Expected fields: 'title', 'reproduction_steps' (list), and 'affected_components'.
    For any field that cannot be extracted from the customer message, return "UNKNOWN_VALUE" for that field.
    Then, constructs a ticket with default values for severity, priority, and assigned_team (all set to "TBD"),
    and assigns a unique bug ID in the format: BUG-<BUG_COUNTER>.
    """
    message = state.get("message", "")
    product = state.get("product", "")

    if product not in config["products"]:
        logger.error("Invalid Product")
        return {"customer_response": "Invalid Product Name", "response_data": {}}

    component_team_mapping = config["products"][product]["component_team_mapping"]
    components_list = component_team_mapping.keys()

    prompt = (
        "You are an expert at extracting bug report details from customer messages. "
        "Extract the following fields from the message: 'title', 'reproduction_steps' (as a list), "
        "and 'affected_components'. For 'affected_components', choose the most appropriate one from the following list: "
        f"{components_list}. "
        "If a field cannot be determined from the message, use the value 'UNKNOWN_VALUE' for that field. "
        "Return your answer as a JSON object with these keys.\n\n"
        f'Customer message: "{message}"'
    )

    messages = [
        {
            "role": "system",
            "content": "You are an expert at extracting structured bug report details.",
        },
        {"role": "user", "content": prompt},
    ]

    llm_client = LLMClient()
    response = llm_client.parse(
        model=config["model"],
        messages=messages,
        response_format=BugReportModel,
    )
    try:
        data = response.model_dump()
        print("data", data)
    except Exception as e:
        logger.error(str(e))
    assigned_teams = [
        component_team_mapping.get(affected_component, "TBD")
        for affected_component in data["affected_components"]
    ]
    global BUG_COUNTER
    ticket = {
        "id": f"BUG-{BUG_COUNTER}",
        "title": data.get("title", ""),
        "reproduction_steps": data.get("reproduction_steps"),
        "affected_components": data.get("affected_components"),
        "severity": "Medium",
        "priority": "High",
        "assigned_team": assigned_teams,
    }
    BUG_COUNTER += 1

    customer_response = f"Thank you for your bug report. Your report has been recorded with ID {ticket['id']}."
    return {"customer_response": customer_response, "response_data": {"ticket": ticket}}
