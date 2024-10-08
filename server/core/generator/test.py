from server.core.generator.generator import CourseCreationAssistant

def main():
    # Initialize the assistant
    assistant = CourseCreationAssistant(conversation_id=None)
    user_selections = {}
    user_needs_guidance = False


    # Start the query process
    print("\n--- Starting Course Selection ---\n")

    while True:
        user_selections, user_needs_guidance = user_selection_with_multiple_options(
            assistant.unit_data, "Unit", user_selections, user_needs_guidance)

        # Ask if the user wants to add more selections or finish
        if not ask_user_to_continue_or_finish():
            break
    # Prepare user_selection structure for sending to process_query
    user_selection_data = {
        "student_selection": {
            "user_needs_guidance": user_needs_guidance,
            "selected_modules": {},  # Populated by user selections
            "available_time": None  # Placeholder, will be filled later
        }
    }

    # Fill in the selected modules and outcomes
    for unit, modules in user_selections.items():
        for module, details in modules.items():
            if "selected_outcomes" in details:
                user_selection_data["student_selection"]["selected_modules"][module] = details["selected_outcomes"]
    

    print('User Selection Data', user_selection_data)

    # Simulate asking for available time (can be set to None for no constraint)
    available_time = input("Available time to study (in minutes) or leave blank for no constraint: ")
    user_selection_data["student_selection"]["available_time"] = int(available_time) if available_time else None



    while True:
        if not assistant.conversation:
            query = 'Help me generate a course'

            if not user_needs_guidance:
                query += ' according to my selection.'
        else:
            query = input('Enter your query (or type "quit" to exit): ')

        if not query:
            print("Invalid input")
            continue

        if query.lower() == 'quit':
            break

        # Process the query with the collected user_selection
        response = assistant.process_query(query, user_selection_data)

        print('\n\n====== Assistant Response =====\n')
        print(response)


def ask_user_to_continue_or_finish():
    """
    Ask the user if they want to make additional selections or finish.
    Returns True if the user wants to make more selections, False if they are done.
    """
    while True:
        user_choice = input("\nDo you want to add more selections or finish? (Type 'add' to make more selections or 'finish' to stop): ").strip().lower()
        if user_choice in ["add", "finish"]:
            return user_choice == "add"
        print("Invalid input. Please type 'add' or 'finish'.")


def user_selection_with_multiple_options(data, level_name="Unit", previous_selection=None, user_needs_guidance=False):
    """
    Function to allow the user to select multiple options from hierarchical data and revisit previous selections.
    If the user selects "can't decide," all child elements of the option are included, and user_needs_guidance is set to True.

    Parameters:
    data (dict): The hierarchical data for the selection (e.g., units, modules, LOs).
    level_name (str): Name of the current level (e.g., "Unit", "Module", "Learning Outcome").
    previous_selection (dict): Stores the previously selected options to allow multiple selections.
    user_needs_guidance (bool): Tracks whether the user needs guidance in selecting content.

    Returns:
    tuple: Updated selections based on user input and a flag indicating if the user needs guidance.
    """
    if previous_selection is None:
        previous_selection = {}

    while True:
        print(f"\nSelect a {level_name} from the following options (type the number or 'can't decide'):")
        options = list(data.keys()) + ["can't decide"]

        # Display options
        for idx, option in enumerate(options, 1):
            print(f"{idx}. {option}")

        # Get user input
        user_input = input(f"\nEnter your choice (1-{len(options)}): ").strip()

        # Check if user input is valid
        try:
            selected_idx = int(user_input)
            if 1 <= selected_idx <= len(options):
                selected_option = options[selected_idx - 1]
                break
        except ValueError:
            print("Invalid input. Please enter a valid number.")

    # Handle "can't decide" case: return all child elements and set guidance flag to True
    if selected_option == "can't decide":
        previous_selection.update(data)
        user_needs_guidance = True  # User needs guidance
        return previous_selection, user_needs_guidance

    # Initialize or update previous selections for the selected unit/module
    if level_name == "Unit":
        if selected_option not in previous_selection:
            previous_selection[selected_option] = {}
        selected_sub_data = data[selected_option]
        module_selection, user_needs_guidance = user_selection_with_multiple_options(
            selected_sub_data, "Module", previous_selection[selected_option], user_needs_guidance)
        previous_selection[selected_option].update(module_selection)

    elif level_name == "Module":
        if selected_option not in previous_selection:
            previous_selection[selected_option] = {}
        selected_sub_data = data[selected_option]
        learning_outcomes = select_learning_outcomes(selected_sub_data, previous_selection[selected_option])
        previous_selection[selected_option].update(learning_outcomes)

    return previous_selection, user_needs_guidance


def select_learning_outcomes(module_data, previous_lo_selection=None):
    """
    Function to allow the user to select learning outcomes from a module and revisit previous selections.

    Parameters:
    module_data (dict): The data for a specific module, containing learning outcomes and other details.
    previous_lo_selection (dict): Stores previously selected learning outcomes.

    Returns:
    dict: Updated selected learning outcomes.
    """
    if previous_lo_selection is None:
        previous_lo_selection = {}

    outcomes = module_data.get("module_outcomes", [])

    # Display the learning outcomes and allow multiple selection
    print("\nSelect Learning Outcomes from the list (you can select multiple by typing numbers separated by commas):")

    for idx, outcome in enumerate(outcomes, 1):
        print(f"{idx}. {outcome}")

    print(f"{len(outcomes) + 1}. can't decide")

    # Get user input for multiple selections
    user_input = input(f"\nEnter your choices (e.g., 1, 3, 5 or {len(outcomes) + 1} for 'can't decide'): ").strip()

    if user_input == str(len(outcomes) + 1):  # User chose 'can't decide'
        previous_lo_selection["selected_outcomes"] = outcomes
        previous_lo_selection["module_prereqs"] = module_data.get("module_prereqs", [])
        previous_lo_selection["cells"] = module_data.get("cells", [])
        return previous_lo_selection

    # Parse the user input and filter the selected outcomes
    selected_indices = [int(x.strip()) for x in user_input.split(",") if x.strip().isdigit()]

    selected_outcomes = [outcomes[i - 1] for i in selected_indices if 1 <= i <= len(outcomes)]

    # Add the new selections to the previous selections
    previous_lo_selection.setdefault("selected_outcomes", []).extend(selected_outcomes)
    previous_lo_selection["module_prereqs"] = module_data.get("module_prereqs", [])
    previous_lo_selection["cells"] = module_data.get("cells", [])

    return previous_lo_selection


if __name__ == "__main__":
    main()
