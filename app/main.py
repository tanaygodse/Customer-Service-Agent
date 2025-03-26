from fastapi import FastAPI
from pydantic import BaseModel
from app.agent import workflow, GraphState
import uvicorn

app = FastAPI()


class CustomerMessageInput(BaseModel):
    customer_id: str
    message: str
    product: str


class CustomerServiceResponse(BaseModel):
    message_type: str
    confidence_score: float
    response_data: dict
    customer_response: str


compiled_app = workflow.compile()


@app.post("/process-customer-message", response_model=CustomerServiceResponse)
async def process_customer_message(input_data: CustomerMessageInput):
    # Initialize the workflow state.
    initial_state: GraphState = {
        "customer_id": input_data.customer_id,
        "message": input_data.message,
        "product": input_data.product,
        "classification": None,
        "confidence_score": None,
        "extraction_data": {},
        "customer_response": None,
        "response_data": {},
    }
    # Await the compiled workflow instance's async invoke.
    result = await compiled_app.ainvoke(initial_state)
    return {
        "message_type": result.get("classification", ""),
        "confidence_score": result.get("confidence_score", 0.0),
        "response_data": result.get("response_data", {}),
        "customer_response": result.get("customer_response", ""),
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
