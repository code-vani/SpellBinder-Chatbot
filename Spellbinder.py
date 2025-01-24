import random
import difflib
import string
import csv
import streamlit as st

# Function to load data from CSV files
def load_csv(filename, encoding='utf-8'):
    """Load data from a CSV file with a specified encoding and return as a list of dictionaries."""
    rows = []
    try:
        with open(filename, 'r', encoding=encoding) as file:
            reader = csv.DictReader(file)
            for row in reader:
                if 'Command' in row and 'Intent' in row:  # Ensure required fields exist
                    rows.append(row)
                elif 'Riddle' in row and 'Answer' in row:  # Special case for riddles
                    rows.append({'Riddle': row['Riddle'], 'Answer': row['Answer']})
                elif 'Input Phrase' in row and 'Response' in row:  # Special case for responses
                    rows.append({'Input Phrase': row['Input Phrase'], 'Response': row['Response']})
                elif 'Question' in row and 'Answer' in row:  # Special case for trivia questions
                    rows.append({'Question': row['Question'], 'Answer': row['Answer']})
                else:
                    print(f"Warning: Missing expected keys in row: {row}")
    except UnicodeDecodeError:
        print(f"Error: Unable to decode the file '{filename}' using {encoding}. Trying with 'ISO-8859-1'.")
        return load_csv(filename, encoding='ISO-8859-1')
    return rows

# Load data from CSV files
spell_commands = load_csv('spell_commands.csv')
trivia_questions = load_csv('trivia_questions.csv')
magical_responses = load_csv('magical_responses.csv')
riddles = load_csv('riddles.csv')

# Define the necessary functions
def normalize_input(user_input):
    """Normalize user input by converting to lowercase, and removing unnecessary punctuation."""
    user_input = user_input.strip().lower().translate(str.maketrans('', '', string.punctuation.replace("'", "").replace("-", "")))
    return user_input

def get_intent(user_input):
    """Match user input to the closest intent using fuzzy matching."""
    commands = [cmd['Command'].strip().lower() for cmd in spell_commands]  # Normalize commands
    user_input_normalized = normalize_input(user_input)  # Normalize user input
    closest_match = difflib.get_close_matches(user_input_normalized, commands, n=1, cutoff=0.7)  # Lower cutoff for more leniency
    
    if closest_match:
        for cmd in spell_commands:
            if cmd['Command'].strip().lower() == closest_match[0]:  # Normalize comparison
                return cmd['Intent']
    return None

# Handle different spell commands and provide responses
def handle_trivia():
    """Ask a random trivia question."""
    question = random.choice(trivia_questions)
    return question['Question'], question['Answer']

def handle_riddles():
    """Ask a random riddle."""
    riddle = random.choice(riddles)
    return riddle['Riddle'], riddle['Answer']

def handle_knowledge():
    """Provide general knowledge."""
    return "Here's a magical fact: The only way to move between different magical realms is by casting a powerful portkey spell."

def handle_history():
    """Provide a historical fact."""
    return "Did you know that the first magical duel ever recorded happened in 1547 between two great wizards?"

def handle_explanation():
    """Provide an explanation for a topic."""
    return "Explanation: The spell 'Alohomora' unlocks doors, but it works only on doors that are magically locked."

def handle_movie():
    """Fetch a random magical movie."""
    movies = ["Harry Potter and the Philosopher's Stone", "Fantastic Beasts and Where to Find Them", "The Sorcerer's Apprentice"]
    return random.choice(movies)

def handle_cheer():
    """Send a cheerful message."""
    return "You are magical, keep up the good work! ✨"

def handle_details():
    """Fetch detailed information."""
    return "The Wizarding World is vast and filled with magic. From wands to spells, there’s so much to explore!"

# comparison in trivia/riddle answers
def check_answer(user_input, correct_answer):
    """Check the user's answer with a lenient comparison."""
    user_input_normalized = normalize_input(user_input)
    correct_answer_normalized = normalize_input(correct_answer)

    # If user input matches the answer with fuzzy matching or exact match
    if difflib.SequenceMatcher(None, user_input_normalized, correct_answer_normalized).ratio() > 0.85:
        return True
    return False

def handle_riddle_mode(user_input):
    """Handle riddle mode with lenient answer matching."""
    if check_answer(user_input, st.session_state.current_riddle_answer):
        st.write("Well done! You've solved the riddle!")
    else:
        st.write(f"Not quite! The answer was '{st.session_state.current_riddle_answer}'.")

def handle_trivia_mode(user_input):
    """Handle trivia mode with lenient answer matching."""
    if check_answer(user_input, st.session_state.current_answer):
        st.write("Correct! You've proven your magical knowledge, wizard!")
    else:
        st.write(f"Oops, that's not quite right. The correct answer was '{st.session_state.current_answer}'. Try another spell or question!")

#get_magical_response function to handle greetings first
def get_magical_response(user_input_normalized):
    """Match user input with magical responses, but avoid matching greetings."""
    # Check for greetings first to avoid them being matched with magical responses
    greetings = ['hi', 'hello', 'hey', 'hru', 'howdy']
    if user_input_normalized in greetings:
        return "Ah, greetings young wizard! How can I assist you on this magical journey?"

    # Now check for magical responses
    for phrase in magical_responses:
        if user_input_normalized in phrase['Input Phrase'].lower():
            return phrase['Response']
    return None  # Return None if no match is found

# Sorting Hat functionality
class SortingHat:
    def __init__(self):
        self.questions = [
            ("What do you value most?", ["Bravery", "Ambition", "Hard work", "Intelligence"]),
            ("Which would you prefer to be known for?", ["Courage", "Power", "Loyalty", "Wit"]),
            ("Pick your favorite activity:", ["Adventure", "Leadership", "Helping others", "Studying"]),
        ]
        self.current_question_index = 0
        self.answers = []

    def get_next_question(self):
        if self.current_question_index < len(self.questions):
            question, options = self.questions[self.current_question_index]
            return question, options
        else:
            return None, None

    def submit_answer(self, answer):
        # Normalize the answer before storing it
        normalized_answer = normalize_input(answer)
        self.answers.append(normalized_answer)
        self.current_question_index += 1

    def get_house(self):
        house_scores = {
            'Gryffindor': self.answers.count('bravery') + self.answers.count('courage') + self.answers.count('adventure'),
            'Slytherin': self.answers.count('ambition') + self.answers.count('power') + self.answers.count('leadership'),
            'Hufflepuff': self.answers.count('hard work') + self.answers.count('loyalty') + self.answers.count('helping others'),
            'Ravenclaw': self.answers.count('intelligence') + self.answers.count('wit') + self.answers.count('studying')
        }
        
        # Debugging: Print the scores for each house
        print("House Scores:", house_scores)

        sorted_house = max(house_scores, key=house_scores.get)
        return f"Congratulations! You have been sorted into {sorted_house}!"
    
st.markdown(
    """
    <style>
    .stApp {
        background-color: #800080;  /* Purple color */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# CSS for styling
css = """
<style>
    .chat-container {
        max-width: 600px;
        margin: auto;
        padding: 20px;
        border: 2px solid gold;  /* Gold border for elegance */
        border-radius: 10px;
        background-color: rgba(255, 255, 255, 0.2);  /* Semi-transparent white for chat container */
        max-height: 500px;  /* Set a maximum height for the chat container */
        overflow-y: auto;  /* Enable vertical scrolling */
    }
    .user-message {
        text-align: right;  /* Right-align user message */
        color: black;  /* User message color (black for contrast against light background) */
        background-color: rgba(255, 165, 0, 0.8);  /* Orange background for user messages */
        padding: 10px;  /* Add padding for better spacing */
        border-radius: 10px;  /* Rounded corners */
        margin: 5px 0;
    }
    .bot-message {
        text-align: left;  /* Left-align bot message */
        color: black;  /* Bot message color (black for contrast) */
        background-color: rgba(0, 191, 255, 0.8);  /* Deep sky blue background for bot messages */
        padding: 10px;  /* Add padding for better spacing */
        border-radius: 10px;  /* Rounded corners */
        margin: 5px 0;
    }
    h1 {
        text-align: center;
        color: gold;  /* Title color */
        text-shadow: 2px 2px 5px rgba(0, 0, 0, 0.5);  /* Add shadow for a glowing effect */
    }
</style>
"""

# Inject CSS
st.markdown(css, unsafe_allow_html=True)

def main():
    st.title("SpellBinder-The Magical Chatbot")

    # Initialize session states
    if 'current_mode' not in st.session_state:
        st.session_state.current_mode = None
    if 'current_question' not in st.session_state:
        st.session_state.current_question = None
    if 'current_answer' not in st.session_state:
        st.session_state.current_answer = None
    if 'current_riddle' not in st.session_state:
        st.session_state.current_riddle = None
    if 'current_riddle_answer' not in st.session_state:
        st.session_state.current_riddle_answer = None
    if 'sorting_hat' not in st.session_state:
        st.session_state.sorting_hat = SortingHat()
    if 'messages' not in st.session_state:
        st.session_state.messages = []  # Store chat messages

    chat_container = st.container()

    user_input = st.text_input("Enter your spell or question:", key="input")

    if user_input:
        user_input_normalized = normalize_input(user_input)

        # Add user message to chat history
        st.session_state.messages.append(f"You: {user_input}")

        # Check for greetings first
        magical_response = get_magical_response(user_input_normalized)
        if magical_response:
            st.session_state.messages.append(f"SpellBinder: {magical_response}")
        else:
            if user_input_normalized in ['hi', 'hello', 'hey', 'hru', 'howdy']:
                response = "Ah, greetings young wizard! How can I assist you on this magical journey?"
                st.session_state.messages.append(f"SpellBinder: {response}")

            # Sorting Hat mode
            elif user_input_normalized == 'sort me':
                st.session_state.current_mode = 'sorting_hat'
                question, options = st.session_state.sorting_hat.get_next_question()
                if question:
                    response = f"{question} ({', '.join(options)})"
                    st.session_state.messages.append(f"SpellBinder: {response}")
                else:
                    st.session_state.messages.append("SpellBinder: You've already been sorted!")

            # If in sorting hat mode, evaluate the answer
            elif st.session_state.current_mode == 'sorting_hat':
                st.session_state.sorting_hat.submit_answer(user_input_normalized)
                question, options = st.session_state.sorting_hat.get_next_question()
                if question:
                    response = f"{question} ({', '.join(options)})"
                    st.session_state.messages.append(f"SpellBinder: {response}")
                else:
                    result = st.session_state.sorting_hat.get_house()
                    st.session_state.messages.append(f"SpellBinder: {result}")
                    st.session_state.current_mode = None  # Reset mode after sorting

            # Handle trivia mode
            elif st.session_state.current_mode == 'trivia':
                normalized_answer = normalize_input(st.session_state.current_answer)
                normalized_user_input = normalize_input(user_input)
                if difflib.SequenceMatcher(None, normalized_user_input, normalized_answer).ratio() > 0.85:
                    response = "Correct! You've proven your magical knowledge, wizard!"
                else:
                    response = f"Oops, that's not quite right. The correct answer was '{st.session_state.current_answer}'. Try another spell or question!"
                st.session_state.messages.append(f"SpellBinder: {response}")
                st.session_state.current_mode = None  # Reset mode to allow new commands

            # Handle riddle mode
            elif st.session_state.current_mode == 'riddle':
                normalized_riddle_answer = normalize_input(st.session_state.current_riddle_answer)
                normalized_user_input = normalize_input(user_input)
                if difflib.SequenceMatcher(None, normalized_user_input, normalized_riddle_answer).ratio() > 0.85:
                    response = "Well done! You've solved the riddle!"
                else:
                    response = f"Not quite! The answer was '{st.session_state.current_riddle_answer}'."
                st.session_state.messages.append(f"SpellBinder: {response}")
                st.session_state.current_mode = None  # Reset mode to allow new commands

            # Process intents for various other commands
            elif user_input_normalized == 'bye':
                response = "Farewell, brave spellcaster! May the winds guide your path."
                st.session_state.messages.append(f"SpellBinder: {response}")
                st.session_state.current_mode = None

            # Process other commands
            else:
                intent = get_intent(user_input_normalized)
                if intent == 'fetch_trivia':
                    current_question, current_answer = handle_trivia()
                    st.session_state.current_mode = 'trivia'
                    st.session_state.current_question = current_question
                    st.session_state.current_answer = current_answer
                    response = f"Here's a trivia question for you: {current_question}"
                    st.session_state.messages.append(f"SpellBinder: {response}")
                elif intent == 'fetch_weather':
                    response = "The weather today is sunny with a hint of magic in the air!"
                    st.session_state.messages.append(f"SpellBinder: {response}")
                elif intent == 'fetch_riddles':
                    current_riddle, current_riddle_answer = handle_riddles()
                    st.session_state.current_mode = 'riddle'
                    st.session_state.current_riddle = current_riddle
                    st.session_state.current_riddle_answer = current_riddle_answer
                    response = f"Here's a riddle for you: {current_riddle}"
                    st.session_state.messages.append(f"SpellBinder: {response}")
                elif intent == 'fetch_knowledge':
                    response = handle_knowledge()
                    st.session_state.messages.append(f"SpellBinder: {response}")
                elif intent == 'fetch_history':
                    response = handle_history()
                    st.session_state.messages.append(f"SpellBinder: {response}")
                elif intent == 'fetch_explanation':
                    response = handle_explanation()
                    st.session_state.messages.append(f"SpellBinder: {response}")
                elif intent == 'fetch_movie':
                    response = handle_movie()
                    st.session_state.messages.append(f"SpellBinder: {response}")
                elif intent == 'cheer_user':
                    response = handle_cheer()
                    st.session_state.messages.append(f"SpellBinder: {response}")
                elif intent == 'end_conversation':
                    response = "Farewell, brave spellcaster! Until we meet again."
                    st.session_state.messages.append(f"SpellBinder: {response}")
                elif intent == 'give_advice':
                    response = "Believe in yourself! You have the power to create your own magic."
                    st.session_state.messages.append(f"SpellBinder: {response}")
                elif intent == 'fetch_fun_fact':
                    response = "Did you know? The first Harry Potter book was published in 1997!"
                    st.session_state.messages.append(f"SpellBinder: {response}")
                elif intent == 'fetch_joke':
                    response = "Why did the wizard break up with his girlfriend? Because she had too many hexes!"
                    st.session_state.messages.append(f"SpellBinder: {response}")
                elif intent == 'fetch_prophecy':
                    response = "Today is a day of great potential. Use your magic wisely!"
                    st.session_state.messages.append(f"SpellBinder: {response}")
                elif intent == 'fetch_details':
                    response = handle_details()
                    st.session_state.messages.append(f"SpellBinder: {response}")
                else:
                    response = "I'm not sure what spell you cast, try again!"
                    st.session_state.messages.append(f"SpellBinder: {response}")

        # Refresh the chat display after user input
        with chat_container:
            for message in st.session_state.messages:
                if message.startswith("You:"):
                    st.markdown(f"<div class='user-message'>{message}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='bot-message'>{message}</div>", unsafe_allow_html=True)
        
        # Add JavaScript to scroll to the bottom of the chat container only if the user is at the bottom
        st.markdown(
            """
            <script>
                const chatContainer = document.querySelector('.chat-container');
        
                // Function to check if the user is at the bottom of the chat container
                function isScrolledToBottom() {
                    return chatContainer.scrollHeight - chatContainer.clientHeight <= chatContainer.scrollTop + 1;
                }

                // Scroll to the bottom if the user is already at the bottom
                if (isScrolledToBottom()) {
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                }
            </script>
            """,
            unsafe_allow_html=True
        )

# Run the app
if __name__ == "__main__":
    main()
