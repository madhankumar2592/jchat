import streamlit as st
import assistant_bot as bot

st.set_page_config(page_title="AIR LEGION")  

# Function to inject custom CSS
def inject_custom_css():
    st.markdown(
        """
<style>
        .stTextArea textarea {
            background-color: #e0f7fa;  /* Light green background for text area */
            border: 1px solid #00796b;  /* Darker green border */
            border-radius: 5px;
        }
        .stButton > button {
            background-color: #00796b;  /* Green button background */
            color: white;  /* Button text color */
            border-radius: 5px;
            padding: 10px 20px;
            border: none;
        }
        .stButton > button:hover {
            background-color: #004d40;  /* Darker green on hover */
        }
        .css-1d391kg {  /* Streamlit's container class */
            background-color: #e0f7fa;  /* Light green background for the entire page */
        }
</style>
        """,
        unsafe_allow_html=True
    )

# Inject custom CSS
inject_custom_css()

st.title("Air Legion")  

# Display a greeting message
st.markdown("<p style='font-size: 16px; color: #555;'>Feel free to ask me anything about the aerospace domain, including cargo!</p>", unsafe_allow_html=True)

# Initialize session state for chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

chat_container = st.container()

# Function to add messages to chat history
def add_message(role, text):
    # Avoid duplicates
    if not st.session_state.chat_history or (st.session_state.chat_history[-1]['role'] != role or st.session_state.chat_history[-1]['text'] != text):
        st.session_state.chat_history.append({"role": role, "text": text})

# Display chat history
with chat_container:
    for message in st.session_state.chat_history:
        st.chat_message(message['role']).markdown(message['text'])

# Input box
input_text = st.chat_input("Chat with your bot here")  # Display a chat input box

if input_text:
    # Add user's message to chat history
    add_message('user', input_text)
    # Get response from bot
    response_content = bot.get_text_response(input_text)
    # Add bot's response to chat history
    add_message('assistant', response_content)
    # Re-render chat history
    with chat_container:
        for message in st.session_state.chat_history:
            st.chat_message(message['role']).markdown(message['text'])
