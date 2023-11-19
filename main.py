import streamlit as st

from adb_functions import list_devices

from langchain_agent import run_agent_executor

from asyncio import Queue


# Main app
def main():
    st.sidebar.title("Options")

    # OpenAI API Key Input
    api_key = st.sidebar.text_input("Enter your OpenAI API Key", type="password")

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

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("What is up?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        # Display assistant response in chat message container

        with st.chat_message("assistant"):
            message_placeholder = st.empty()

            # Augment the prompt with the current selected serial number and output path.
            prompt = f"{prompt} using this device serial number: {selected_device} and if you must save anything, use this output path: {output_folder}"

            response_queue = Queue()
            run_agent_executor(prompt, api_key, response_queue)

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
