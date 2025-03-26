from openai import OpenAI
import logging

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self):
        self.client = OpenAI()

    def parse(self, model: str, messages: list, response_format=None):
        """
        Makes an API call to OpenAI's chat completions endpoint with the given parameters.
        Returns the parsed output (assumed to have a .json() method that returns a JSON-formatted string).
        """
        try:
            response = self.client.beta.chat.completions.parse(
                model=model, messages=messages, response_format=response_format
            )
            # Retrieve the parsed output from the response.
            output = response.choices[0].message.parsed
            return output
        except Exception as e:
            logger.error(f"LLM API call failed: {str(e)}")
            raise
