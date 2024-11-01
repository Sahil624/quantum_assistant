from typing import Optional, List, Tuple, Dict
import json
from server.core.base.config import config
from server.core.base.conversation import Conversation
from server.core.generator.consts import UNIT_MAPPING

class CourseCreationAssistant(Conversation):
    """
    A class for interacting with Anthropic Claude to generate personalized course plans based on the user's input.
    
    Inherits from the `Conversation` abstract class.
    
    Attributes:
    - unit_data: The structured data for units, modules, and learning outcomes.
    - user_selections: The user's selections for units, modules, and learning outcomes.
    - user_needs_guidance: Whether the user needs guidance in selecting the course content.
    - final_input_data: The data structure that is sent to Claude for generating a course.
    """

    unit_mapping = UNIT_MAPPING

    response_tags = [
        "selected_content",
        "course_summary",
        "guidance_conversation",
        "user_needs_guidance_change"
    ]

    def __init__(self, conversation_id: Optional[str] = None):
        super().__init__(conversation_id)
        self.unit_data = self.generate_unit_data(
            config['notebook_json_path'],
            config['cell_json_path']
        )

    def generate_unit_data(self, notebook_json_path: str, cell_json_path: str) -> Dict[str, Dict]:
        """
        Generates the unit_data from the given notebook and cell JSON files.

        Parameters:
        - notebook_json_path (str): Path to the notebook data JSON file.
        - cell_json_path (str): Path to the cell data JSON file.

        Returns:
        - dict: Structured data containing units, modules, outcomes, and cells.
        """
        with open(notebook_json_path, 'r') as notebook_file:
            notebook_data = json.load(notebook_file)

        with open(cell_json_path, 'r') as cell_file:
            cell_data = json.load(cell_file)

        unit_data = {}

        for unit, modules in self.unit_mapping.items():
            unit_data[unit] = {}

            for module in modules:
                if module in notebook_data:
                    module_info = notebook_data[module]

                    # Prepare module structure
                    unit_data[unit][module] = {
                        "module_outcomes": module_info.get("module_outcomes", []),
                        "module_prereqs": module_info.get("module_prereqs", []),
                        "cells": []
                    }

                    # Map cells based on the cell_data for this module
                    if module in cell_data:
                        for cell in cell_data[module]:
                            cell_id = cell.get("metadata", {}).get("cell_details", {}).get("cell_ID")
                            if cell_id:
                                unit_data[unit][module]["cells"].append(cell_id)

        return unit_data
    
    def generate_final_input_data(self, user_selection: Dict) -> Dict:
        """
        Generates the final input data structure based on the user_selection provided by the webserver.

        Parameters:
        - user_selection (dict): Data from the webserver with selected learning outcomes, available time, and whether the user needs guidance.

        The user_selection structure is expected to look like this:
        {
            "student_selection": {
                "user_needs_guidance": bool,
                "selected_modules": {
                    "Module Name": [
                        "Learning Outcome 1",
                        "Learning Outcome 2"
                    ]
                },
                "available_time": int  # Can be None if no time constraint
            }
        }

        Returns:
        - dict: Final input data for Claude.
        """
        user_needs_guidance = user_selection["student_selection"]["user_needs_guidance"]
        selected_modules = user_selection["student_selection"]["selected_modules"]
        available_time = user_selection["student_selection"].get("available_time", None)

        # Initialize the final input data structure
        final_input_data = {
            "student_selection": {
                "user_needs_guidance": user_needs_guidance,
                "selected_modules": selected_modules,
                "available_time": available_time if available_time is not None else "No time constraint"
            },
            "input_data": {
                "unit_data": {}  # We'll populate this with the complete unit, module, and cell metadata.
            }
        }

        # If user needs guidance, include all available data
        if user_needs_guidance:
            final_input_data["input_data"]["unit_data"] = self.unit_data
        else:
            # Iterate over the selected modules to extract corresponding data from unit_data (self.unit_data)
            for module_name, selected_outcomes in selected_modules.items():
                for unit_name, modules in self.unit_data.items():
                    if module_name in modules:
                        module_info = self.unit_data[unit_name][module_name]

                        # Only include necessary information (module_outcomes, cells, etc.)
                        final_input_data["input_data"]["unit_data"].setdefault(unit_name, {})[module_name] = {
                            "module_outcomes": module_info.get("module_outcomes", []),
                            "module_prereqs": module_info.get("module_prereqs", []),
                            "cells": module_info.get("cells", [])
                        }

        return final_input_data



    def prepare_system_prompt(self, query, user_selection) -> str:
        """
        Prepares the Claude system prompt based on the final input data.

        This method uses the generator prompt you provided earlier.

        Returns:
        - str: The Claude prompt with formatted JSON data.
        """

        final_input_data = self.generate_final_input_data(user_selection)

        claude_prompt = f'''
        You are an advanced course creation assistant tasked with helping users create personalized learning paths. Your goal is to either select appropriate content based on the user's choices or guide the user through the selection process, depending on their ability to decide.

        You will receive two main inputs in this system prompt:

        <student_selection>
        {json.dumps(final_input_data.get('student_selection', ''))}
        </student_selection>

        <input_data>
        {json.dumps(final_input_data.get('input_data'))}
        </input_data>

        First, analyze the student_selection to determine if the user needs guidance or has already made their selections. Then, process the input_data to understand the course structure and content.

        If the user can decide (user_needs_guidance is false):

        1. Identify the selected modules from the student_selection.
        2. Calculate the total time required for the selected modules and their prerequisites using the cell_estimated_time from the input_data.
        3. If the total time exceeds the available_time:
           a. Prioritize the most important learning outcomes and prerequisite cells.
              a1. Prerequisites for the selected modules.
              a2. Core concepts within the selected modules.
              a3. Quiz content for reinforcing key concepts.
           b. Remove less critical content such as review material, extra quizzes, or additional examples until the total time fits within the available_time. c. In cases where multiple learning outcomes or modules are of equal priority, select the content with the shortest estimated time to ensure that more topics can fit into the available_time.
           c. Remove less critical content until the total time fits within the available_time.
        4. Compile a list of cell_IDs that fit within the time constraint.
           a. Include the total estimated course duration and mention whether there is any remaining time, or if all the available time is used.
        5. Prepare a brief summary of the generated course.
        6. If the total time fits within the available_time and there is remaining time, ask the user if they would like to add any more content or if they are satisfied with the course plan.
        7. In this case no need to guide student for course selection as student has already selected topics. In this case, the only goad is to generate course according to time limit (If any).

        If the user needs guidance (user_needs_guidance is true):

        1. Start by asking the user about their learning goals, areas of interest, and current level of knowledge. Use the following questions as a guide:
           - What specific topics are you most interested in learning about?
           - How would you describe your current level of knowledge in this subject area?
           - Are there any particular skills you're hoping to develop through this course?
        2. Based on their responses, recommend appropriate units and modules from the input_data.
        3. Help the user narrow down their choices by explaining the content and benefits of each recommended module.
        4. Once the user has made their selections, follow the same process as for users who can decide (steps 2-5 above).
        5. Make sure to ask the student how much time they have for learning (in minutes), even if the system prompt says "No time constraint". There might be a possibility that the user has no time constraint but still needs to confirm this.

        Special cases:
        If no content can fit within the available_time or all content is essential and cannot be removed, notify the user and suggest extending the available time or reducing the course scope.

        Output your response in the following format:

        <course_plan>
        <selected_content>
        [List of selected cell_IDs and their associated cell_estimated_time] For example ["m1-LearningOutcomes", "m1-warmup", "m1-background", "m1-imaginaryNumbers"]
        </selected_content>

        <course_summary>
        [Brief summary of the generated course, including selected modules and estimated course duration]
        </course_summary>
        </course_plan>

        If you needed to guide the user through the selection process, include your conversation before the course_plan. In this case course_plan will not be finalized before this process is completed. One first course plan is generated, You should clearly mention that a course is generated, please review and let me know if some adjustment is needed. This should be properly highlighted:
        <guidance_conversation>
        [Your questions and the user's responses]
        </guidance_conversation>

        If within the conversation, the user shifted from user_needs_guidance false to true, send this in response because in that case I will update input_data to send whole data.
        <user_needs_guidance_change>
        true/false according to change
        </user_needs_guidance_change>

        Remember to use only the information provided in the student_selection and input_data. Do not make assumptions or use external knowledge about course content or structure.
        '''
        return claude_prompt

    def process_query(self, query: str, user_selection: Dict[str, str]) -> str:
        """
        Process the query to generate a response from Claude.

        Parameters:
        - query (str): The user's query.

        Returns:
        - str: The response from Claude.
        """
        system_prompt = self.prepare_system_prompt(query, user_selection)
        internal_query = self.prepare_user_prompt(query)

        print(system_prompt)
        print('\n\n')
        print(internal_query)

        self.add_message("user", internal_query)

        response, tags = self.send_to_claude_api(system_prompt)

        print('TAGS', tags)

        self.add_message("assistant", response)

        return response

    def prepare_user_prompt(self, query: str) -> str:
        return f'''                
            <input>
            <user_query>
                {query}
            </user_query>
            </input>
        '''

    def save_to_db(self):
        """
        Placeholder for saving the conversation to a database.
        """
        print(f"Saving conversation {self.conversation_id} to the database.")
        # Implement your database save logic here

    @classmethod
    def load_from_db(cls, conversation_id: str):
        """
        Placeholder for loading the conversation from a database.
        
        Parameters:
        - conversation_id (str): The ID of the conversation to load.

        Returns:
        - CourseCreationAssistant: The loaded conversation instance.
        """
        print(f"Loading conversation {conversation_id} from the database.")
        conversation = cls(conversation_id)
        # Implement your database load logic here and populate conversation.messages
        return conversation
