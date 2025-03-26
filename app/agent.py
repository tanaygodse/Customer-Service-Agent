from typing import Optional, Dict, TypedDict
from langgraph.graph import StateGraph, END

# Import our nodes.
from app.nodes.classification import classify_input_node
from app.nodes.bug_report import bug_report_extraction_node
from app.nodes.feature_request import feature_request_extraction_node
from app.nodes.general_inquiry import general_inquiry_extraction_node


# Define the state used throughout the workflow.
class GraphState(TypedDict):
    customer_id: Optional[str]
    message: Optional[str]
    product: Optional[str]
    classification: Optional[str]
    confidence_score: Optional[float]
    extraction_data: Optional[Dict]
    customer_response: Optional[str]
    response_data: Optional[Dict]


# Initialize the workflow with our GraphState.
workflow = StateGraph(GraphState)

# Add nodes to the workflow.
workflow.add_node("classify_input", classify_input_node)
workflow.add_node("bug_extraction", bug_report_extraction_node)
workflow.add_node("feature_extraction", feature_request_extraction_node)
workflow.add_node("inquiry_extraction", general_inquiry_extraction_node)


# This function determines which extraction node to call based on classification.
def decide_extraction_node(state: GraphState) -> str:
    classification = state.get("classification")
    if classification == "bug_report":
        return "bug_extraction"
    elif classification == "feature_request":
        return "feature_extraction"
    elif classification == "general_inquiry":
        return "inquiry_extraction"
    else:
        # If the classification was not possible, we treat the message as an general inquiry
        return "inquiry_extraction"


# Conditional Edge to send the input to the appropriate node
workflow.add_conditional_edges(
    "classify_input",
    decide_extraction_node,
    {
        "bug_extraction": "bug_extraction",
        "feature_extraction": "feature_extraction",
        "inquiry_extraction": "inquiry_extraction",
    },
)

# All the nodes lead to END
workflow.add_edge("bug_extraction", END)
workflow.add_edge("feature_extraction", END)
workflow.add_edge("inquiry_extraction", END)

# Define entry point as classification node
workflow.set_entry_point("classify_input")
