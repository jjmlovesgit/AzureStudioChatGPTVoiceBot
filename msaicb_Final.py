import streamlit as st
from streamlit_chat import message
import os
import tempfile
import azure.cognitiveservices.speech as speechsdk
import openai
import config
import winsound
import textwrap
from IPython.display import display, Audio
import streamlit as st
from IPython.display import Video
from IPython.display import HTML
import base64

# Provide the path to your logo image file
logo = "https://media.discordapp.net/attachments/995431274267279440/1108765311802556456/YellowArrow_PDFs_to_Custom_Chat_Bot_app_illustration_for_a_cove_e8cb1bda-8b00-48df-b8a3-7f41b7ea4d03.png"


# Provide the path to your video file
video_file_path = "C:/Projects/MS/Studio/VoAIce-main/VoAIce-main/MSCB.mp4"

# Read the video file as bytes
video_bytes = open(video_file_path, "rb").read()

# Encode the video bytes as base64
video_base64 = base64.b64encode(video_bytes).decode("utf-8")

# Generate the HTML video tag with auto-play
video_tag = f"""<video width="250" height="250" controls autoplay>
    <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
    Your browser does not support the video tag.
</video>
"""

# Display the video using Streamlit
st.write(video_tag, unsafe_allow_html=True)

# Apply CSS styling to center the video
st.markdown(
    """
    <style>
    video {
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown(
    """
    <div style="display: flex; justify-content: center;">
        <img src="{}" style="width:250px;height:250px;">
    </div>
    <hr style='border: none; border-top: 1px solid #ccc; margin: 20px 0px;'>
    """.format(logo),
    unsafe_allow_html=True,
)

# Define the robot emoji
robot_emoji = "�"

def transcribe_audio(speech_config):
    audio_config = speechsdk.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    result = speech_recognizer.recognize_once_async().get()
    return result.text.strip()

def generate_response(input_text, conversation_history):
    messages = [
        {"role": "system", "content": "You are a helpful assistant. Please respond to all input in 50 words or less."},
    ]

    messages.extend(conversation_history)
    messages.append({"role": "user", "content": input_text})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=1.3,
    )

    return response['choices'][0]['message']['content']

def synthesize_and_save_speech(speech_config, response_text, file_path):
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
    result = speech_synthesizer.speak_text_async(response_text).get()

    with open(file_path, "wb") as f:
        f.write(result.audio_data)

def play_audio(audio_file_path):
    display(Audio(audio_file_path))

def remove_temp_files(file_path):
    os.remove(file_path)

def main(stop_keyword="stop", exit_keyword="exit"):
    st.title("🤖 ChatGPT Voice Assistant Powered by Azure Speech Studio")

    # Define speech config
    azure_api_key = config.azure_api_key
    azure_region = config.azure_region
    voice = "en-US-ChristopherNeural"
    speech_config = speechsdk.SpeechConfig(subscription=azure_api_key, region=azure_region)
    speech_config.speech_synthesis_voice_name = voice
    openai.api_key = config.openai_api_key

    conversation_history = []

    # Increase font size
    st.markdown("<style>body {font-size: 18px;}</style>", unsafe_allow_html=True)

    # Sidebar button to start the program
    st.sidebar.write("Press the 'Start Button' and ask me a question and I will respond...")  # Instruction section
    if st.sidebar.button("Start Program"):
       # st.sidebar.write("Please ask me a question and I will respond...")  # Instruction section
        st.sidebar.write("Note:  You can start your question over by saying 'Stop' during question input...")  # Instruction section
        st.sidebar.write("You can end the chat session by saying 'Exit'")  # Instruction section
        while True:
            st.text(robot_emoji + " Listening...")
            winsound.Beep(800, 200)  # Play a beep sound when ready for input

            input_text = transcribe_audio(speech_config)
            wrapped_input = textwrap.fill(input_text, width=90)
            indented_input = "\n".join(["<div style='text-align: left;'>" + line + "</div>" for line in wrapped_input.splitlines()])

            st.markdown(f"<div style='padding: 30px;'>"
                        f"<div style='background-color: blue; padding: 10px; border-radius: 5px; color: white; text-align: left;'>"
                        f"{indented_input}</div>"
                        f"</div>",
                        unsafe_allow_html=True)

            if stop_keyword.lower() in input_text.lower():
                st.text("Restarting prompt...")
                conversation_history = []
                continue

            if exit_keyword.lower() in input_text.lower():
                st.markdown(f"<div style='background-color: white; padding: 10px; border-radius: 5px;'>"
                            f"<span style='color: black;'>Goodbye for now...</span></div>",
                            unsafe_allow_html=True)
                break

            response_text = generate_response(input_text, conversation_history)
            wrapped_response = textwrap.fill(response_text, width=70)
            indented_response = "\n".join(["<div style='text-align: left;'>" + line + "</div>" for line in wrapped_response.splitlines()])

            st.markdown(f"<div style='background-color: #ADD8E6; padding: 10px; border-radius: 5px; text-align: left; color: black;'>"
                        f"{indented_response}</div>",
                        unsafe_allow_html=True)

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                audio_file_path = f.name

            try:
                synthesize_and_save_speech(speech_config, response_text, audio_file_path)
                play_audio(audio_file_path)
                remove_temp_files(audio_file_path)
            except Exception as e:
                st.error(f"Error: Failed to generate or play audio - {e}")

            conversation_history.append({"role": "user", "content": input_text})
            conversation_history.append({"role": "assistant", "content": response_text})

if __name__ == "__main__":
    main(stop_keyword="stop", exit_keyword="exit")
