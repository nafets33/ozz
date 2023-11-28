# PyAudio
# brew install flac
# brew install mpv
import streamlit as st
import speech_recognition as sr
import time 
from dotenv import load_dotenv
import os
from elevenlabs import set_api_key
from elevenlabs import Voice, VoiceSettings, generate
from elevenlabs import generate, stream
from custom_button import cust_Button
from streamlit_player import st_player
from utils.main_utils import ozz_master_root

load_dotenv()

def text_stream():
    yield "Hi there, I'm Eleven "
    yield "I'm a text to speech API "



set_api_key(os.environ.get("api_elevenlabs"))

# audio_stream = generate(
#     text=text_stream(),
#     voice="Nicole",
#     model="eleven_monolingual_v1",
#     stream=True
# )

# stream(audio_stream)

# Initialize Streamlit app
st.title("Hey its Hoots and Hootie")

# Initialize the recognizer
recognizer = sr.Recognizer()

hey_hooty = ["hootie", "hey hootie", "hey hooty", "hey hoots", "hey", "play hootie", "hey hoots", "hey hoot"]


story_1 = """
Once upon a moonlit night in a dense forest, there lived a small and timid mouse named Milo. Milo was known far and wide as the cleverest mouse in the entire forest, but he had a problem. You see, Milo was not only clever, but he was also very curious. This curiosity often led him into trouble, and on this particular night, he found himself in a rather perilous situation.
Milo had heard stories of a wise and mysterious owl named Olivia, who resided high up in the tallest tree in the forest. The other animals whispered that Olivia possessed knowledge of the world beyond the forest, and Milo's curiosity got the better of him. He decided to climb up to Olivia's tree to ask her about the world outside.
As he made his way up the towering tree, Milo's heart raced with anticipation and a touch of fear. When he finally reached the top, he found Olivia perched gracefully on a branch, her large, golden eyes gleaming in the moonlight.
"Who dares to disturb my solitude?" hooted Olivia, her voice echoing through the forest.
Milo, though trembling with fear, spoke up, "It's me, Milo, the mouse. I've come to seek your wisdom, dear owl."
Olivia, with a bemused look, leaned closer to inspect the little mouse. She could have easily made a meal out of him, but there was something about his determination that intrigued her. "What wisdom do you seek, little one?"
Milo explained his burning desire to know about the world beyond the forest, the oceans, and the mountains. He had heard that Olivia had seen these wonders and hoped she could share her knowledge.
Olivia, initially tempted to eat the mouse, found herself touched by his innocent curiosity. Instead of making a meal out of Milo, she decided to show him the world herself.
So, Olivia and Milo embarked on an incredible adventure. They soared high above the forest, and Milo marveled at the vastness of the world. He saw sparkling oceans, towering mountains, and endless landscapes. Along the way, Olivia shared stories of her travels and the wonders she had seen.
As the days turned into weeks, Olivia and Milo's friendship grew stronger. They encountered thunderstorms, crossed deserts, and explored dense jungles. Olivia realized that she no longer desired to eat Milo but instead cherished their companionship.
One day, as they watched a breathtaking sunset over a serene lake, Olivia turned to Milo and said, "Milo, I must confess something. When you first climbed up to my tree, I had intended to eat you. But your curiosity and bravery have changed my heart. You are a dear friend, and I am grateful for our adventures together."
Milo smiled warmly at Olivia, "And you, dear Olivia, have shown me a world I could only dream of. You are not only wise but kind-hearted, and I am grateful for your friendship as well."
From that moment on, Olivia and Milo were inseparable. They continued their journey, exploring the world together, and their friendship blossomed into something truly magical. They met creatures from all corners of the Earth, and wherever they went, their unique bond inspired others to put aside their differences and build friendships.
Olivia, the once-mighty owl, and Milo, the clever mouse, had shown the world that even the most unexpected friendships could be the most beautiful. They traveled the world as best friends, spreading the message that kindness and curiosity could bridge any divide and bring the most wonderful adventures to life.
"""

story_1 = """
I have the perfect story! let me get it for you....
"""

def handle_prompt(text):
    # what question was asked?
    # starting a conversation or asking to tell a story?
    # return intent of question
    # ask llm to figure out what the question is to direct response or action

    return text


s_button = st.button("Story") # set session state for rerun to then return new page with adventure story?                        
if s_button:
    audio_stream = generate(
    text=story_1,
    stream=True,
    voice= 'Mimi', #'Charlotte', 'Fin'
    )
    stream(audio_stream)

    st_player("https://www.youtube.com/watch?v=W8EXJ8Gqf0c", playing=True)

# Create a function to listen for the keyword
def listen_for_keyword(conv=False):
    with sr.Microphone() as source:
        with listening.container():
            st.info("Listening...")
        audio = recognizer.listen(source)
        # print(vars(recognizer))

    try:
        # Recognize the keyword
        keyword = recognizer.recognize_google(audio)
        print(keyword)

        if conv:
            return keyword

        keyword_l = keyword.split()[0]
        
        if keyword_l.lower() in hey_hooty:
            st.success("Keyword detected!")

            return keyword
        else:
            # print("not")
            return False


    except sr.UnknownValueError:
        pass
    except sr.RequestError as e:
        st.error(f"Could not request results; {e}")
    return False

# Create a placeholder to display status
output = st.empty()
listening = st.empty()

# Trigger keyword detection and audio recording when the app loads
cust_Button(file_path_url='misc/woots_jumps_once.gif', height='200px', hoverText='', key='hoots_main')
if st.button("listen"):

    lc=0
    # while True:
    keyword = listen_for_keyword()
    if keyword:
        text = handle_prompt(keyword)
        if [i for i in keyword.split() if 'story' in i.lower()]:
            audio_stream = generate(
            text="what kind of story would you like to hear, adventure, mystery, I can make up stories if you like",
            stream=True,
            voice= 'Mimi', #'Charlotte', 'Fin'
            )
            stream(audio_stream)

            # keyword = listen_for_keyword(conv=True)

            # # if keyword:
            # # text = handle_prompt(keyword)
            # audio_stream = generate(
            # text="wonderful story!  I know this wonderful fairy who tells the story wonderfully! ",
            # stream=True,
            # voice= 'Mimi', #'Charlotte', 'Fin'
            # )
            # stream(audio_stream)

            audio_stream = generate(
            text="Lets listen to snow white this time ! I love that story ",
            stream=True,
            voice= 'Fin', #'Charlotte', 'Fin'
            )
            stream(audio_stream)

            st_player("https://www.youtube.com/watch?v=-DHqDPVezRc")
            # st_player("https://www.youtube.com/watch?v=W8EXJ8Gqf0c")
                # if [i for i in keyword.split() if 'sleeping' in i.lower()]:

        
            # s_button = st.button("Adventure Story") # set session state for rerun to then return new page with adventure story?
            
            # with sr.Microphone() as source:
            #     st.info("Listening for 'hey hooty'...")
            #     audio = recognizer.listen(source)
        else:
            audio_stream = generate(
            text="ok tell me more -- or tell me what you're looking for?",
            stream=True,
            voice= 'Mimi', #'Charlotte', 'Fin'
            ) 
            stream(audio_stream)
    
    
    
    lc += 1
    with output.container():
        st.write("write loop count", lc)
            
            # keyword = recognizer.recognize_google(audio)
            
            
            # audio_stream = generate(
            # text=story_1,
            # stream=True,
            # voice= 'Mimi', #'Charlotte', 'Fin'
            # )

            # stream(audio_stream)

        # output.text("Recording audio...")
        # with sr.Microphone() as source:
        #     audio = recognizer.listen(source)

        # try:
        #     # # Save the recorded audio to a file or process it as needed
        #     # with open("recorded_audio.wav", "wb") as f:
        #     #     f.write(audio.get_wav_data())
        #     # st.success("Audio recorded successfully.")
        #     print(audio)
        #     st.write(audio)
        # except Exception as e:
        #     st.error(f"Error recording audio: {e}")
    
    # time.sleep(1)



# audio = generate(
#     text="Hello! My name is Bella.",
#     voice=Voice(
#         voice_id='EXAVITQu4vr4xnSDxMaL',
#         settings=VoiceSettings(stability=0.71, similarity_boost=0.5, style=0.0, use_speaker_boost=True)
#     )
# )

# play(audio)

# ep = st.empty()
# def listen_for_keyword(keyword, lp):
#     r = sr.Recognizer()
#     with sr.Microphone() as source:
#         r.adjust_for_ambient_noise(source)
#         while True:
#             # st.write("Listening...")
#             with ep.container():
#                 st.write("listening loop", lp)
#             audio = r.listen(source)
#             # st.write("Transcribing...")
#             try:
#                 text = r.recognize_google(audio)
#                 print(text)
#                 if keyword in text:
#                     st.write(f"Keyword '{keyword}' detected!")
#                     # Trigger actions based on keyword here
#                     return text
#             except sr.UnknownValueError:
#                 # st.write("Could not understand audio")
#                 pass
#             except sr.RequestError as e:
#                 st.write(f"Could not request results from Google Speech Recognition service; {e}")

# keyword = "hootie"
# lp = 0
# while True:
#     text = listen_for_keyword(keyword, lp)
#     audio_stream = generate(
#     text=story_1,
#     stream=True,
#     voice= 'Mimi', #'Charlotte', 'Fin'
#     )
#     stream(audio_stream)
#     lp+=1