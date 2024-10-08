import re

import anthropic
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Dict
import uuid

from ..base.config import config


class Conversation(ABC):
    # Define the tags we're looking for in API response
    response_tags = []
    debug_print = True

    def __init__(self, conversation_id: Optional[str] = None):
        # self.conversation_id = conversation_id or str(uuid.uuid4())
        self.conversation: List[Dict[str, str]] = []
        self.api_key = config['anthropic_api_key']
        self.anthropic_client = anthropic.Anthropic(api_key=self.api_key)

    @abstractmethod
    def process_query(self, query: str) -> str:
        pass

    @abstractmethod
    def prepare_system_prompt(self, query: str, context: List[Tuple[str, float]]) -> str:
        pass

    @abstractmethod
    def prepare_user_prompt(self, query: str, context: str, **kwargs) -> str:
        pass

    def add_message(self, role: str, content: str):
        self.conversation.append({"role": role, "content": content})

    # @abstractmethod
    def save_to_db(self):
        pass

    @classmethod
    @abstractmethod
    def load_from_db(cls, conversation_id: str):
        pass

    def send_to_claude_api(self, system_prompt) -> Tuple[str, Dict[str, str]]:
        response = None
        try:
            response = self.anthropic_client.messages.create(
                model=config['anthropic_model'],
                system=system_prompt,
                max_tokens=1000,
                messages=self.conversation
            )
        except anthropic.AnthropicError as e:
            print("AnthropicError in anthropic API", e)
            print(str(e))
        except Exception as e:
            print("Exception in anthropic API", e)
            print(str(e))

        if response is None:
            raise Exception("Internal Error")

        try:
            # Extract Claude's response
            if self.debug_print:
                print('\n\n----------------- Anthropic Raw Response -----------------------')
                print("Raw Response\n", response)
                print('----------------------------------------\n\n')

            claude_response = response.content[0].text
            tags = self.extract_tags(claude_response)
            if self.debug_print:
                print('\n\n-------------- Extracted Tags from API --------------------------')
                print("Extracted Tags\n", tags)
                print('----------------------------------------\n\n')

            return claude_response, tags
        except Exception as e:
            print("Exception in anthropic response parsing", e)
            print(str(e))

            raise Exception("Internal Error")

    def extract_tags(self, response: str) -> Dict[str, str]:

        # Initialize the result dictionary
        result = {}

        # Extract content for each tag
        for tag in self.response_tags:
            pattern = f"<{tag}>(.*?)</{tag}>"
            match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
            if match:
                # Strip leading/trailing whitespace and remove extra newlines
                content = re.sub(r'\n+', '\n', match.group(1).strip())
                result[tag] = content

        return result
