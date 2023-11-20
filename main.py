import streamlit as st

from adb_functions import list_devices

from langchain_agent import run_agent_executor

from asyncio import Queue


# Main app
def main():
    st.sidebar.title("Options")

    # OpenAI API Key Input
    api_key = st.sidebar.text_input("Enter your OpenAI API Key", type="password")

    selected_model = st.sidebar.selectbox(
        "Select a Model", ["gpt-4-0613", "gpt-3.5-turbo-0613"]
    )

    # Absolute path output directory
    output_folder = st.sidebar.text_input(
        "Enter the absolute path to a folder where screenshots and reports will be saved to"
    )

    # Device Selection Dropdown
    devices = list_devices()
    selected_device = st.sidebar.selectbox("Select a Device", devices)

    # Horizontal rule on the sidebar
    st.sidebar.markdown("---")

    # Description in the sidebar
    st.sidebar.markdown(
        """
        This tool is a UI chatbot interface for the [Android Debug Bridge](https://developer.android.com/tools/adb) tool (adb).

        Created by [Jack Gordley](https://gordles.io/) for the CS-8395 Digital Forensics course at [Vanderbilt University](https://www.vanderbilt.edu/) Fall 2023.
        """
    )

    # Chat Interface
    st.title(":iphone: Android Debug Bridge Chat")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

        greeting_string = """
Welcome to Android Debug Bridge (adb) chat :sunglasses:. I'm here to help you with your Android forensics investigation. You can start by asking for some common actions:
- What is my current devices battery percentage?
- Can you give me some basic information about my device?
- Can you take a screenshot of my devices current screen?
"""
        st.session_state.messages.append(
            {"role": "assistant", "content": greeting_string}
        )

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if len(devices) == 0:
        with st.chat_message("assistant"):
            st.markdown(
                """
I can't find any devices connected to your computer :disappointed:. Please make sure you have adb installed and running and your device is connected via USB with developer options enabled.
- [Android Docs: Installing and running adb for the first time](https://developer.android.com/tools/adb)
- [Android Docs: Setting up a device for development](https://developer.android.com/studio/debug/dev-options)
"""
            )

    # Accept user input
    if prompt := st.chat_input("Tell me some information about my selected device..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # If api_key or output_folder is not set, display error message
        if not api_key or not output_folder:
            with st.chat_message("assistant"):
                st.markdown(
                    "Please enter your OpenAI API Key and an output folder in the sidebar, I can't function without these :disappointed:"
                )
            return

        with st.chat_message("assistant"):
            message_placeholder = st.empty()

            # Augment the prompt with the current selected serial number and output path.
            prompt = f"{prompt} using this device serial number: {selected_device} and if you must save anything, use this output path: {output_folder}"

            response_queue = Queue()
            run_agent_executor(prompt, api_key, selected_model, response_queue)

            # Get messages from the asyncio queue until we get "[DONE]"
            new_messages = []
            while True:
                message = response_queue.get_nowait()
                if message == "[DONE]":
                    break
                new_messages.append(message)

            complete_string = "\n".join(reversed(new_messages))
            print(complete_string)
            message_placeholder.markdown(complete_string)
            st.session_state.messages.append(
                {"role": "assistant", "content": complete_string}
            )


if __name__ == "__main__":
    main()
