import streamlit as st
from youtubesearchpython import VideosSearch, Video
import os
from master_ozz.utils import init_user_session_state, init_constants, load_local_json, save_json, llm_assistant_response
from ozz_auth import all_page_auth_signin

def get_youtube_video_metadata(url):
    return Video.getInfo(url)

# def search_youtube():
#     channelsSearch = ChannelsSearch('NoCopyrightSounds', limit = 10, region = 'US')

#     print(channelsSearch.result())

#     video = Video.get('https://www.youtube.com/watch?v=z0GKGpObgPY', mode = ResultMode.json, get_upload_date=True)
#     print(video)
#     videoInfo = Video.getInfo('https://youtu.be/z0GKGpObgPY', mode = ResultMode.json)
#     print(videoInfo)
#     videoFormats = Video.getFormats('z0GKGpObgPY')
#     print(videoFormats)



#     channel_id = "UC_aEa8K-EOJ3D6gOs7HcyNg"
#     playlist = Playlist(playlist_from_channel_id(channel_id))

#     print(f'Videos Retrieved: {len(playlist.videos)}')

#     while playlist.hasMoreVideos:
#         print('Getting more videos...')
#         playlist.getNextVideos()
#         print(f'Videos Retrieved: {len(playlist.videos)}')

#     print('Found all the videos.')

def search_youtube(search_query='story book reads', max_results=5):
    """
    Search YouTube for videos based on the given query.

    Parameters:
    - search_query (str): The search query.
    - max_results (int): The maximum number of results to retrieve (default is 5).

    Returns:
    - list: A list of dictionaries, each containing information about a video.
    """
    videos_search = VideosSearch(search_query, limit=max_results)

    results = []
    for result in videos_search.result()["result"]:
        video_info = {
            "title": result["title"],
            "link": result["link"],
            "duration": result["duration"],
            "views": result.get("views", None),  # Use get method to handle KeyError
            "thumbnails": result["thumbnails"],
        }
        results.append(video_info)

    return results


def get_channel_videos_info(channel_url, output_file="output.txt"):
    # Search for videos in the given channel
    videos_search = VideosSearch(channel_url, limit=20)
    results = videos_search.result()['result']

    # Check if the output file exists; if not, create it
    if not os.path.isfile(output_file):
        with open(output_file, 'w', encoding='utf-8') as new_file:
            new_file.write("Video Information:\n\n")

    # Extract and save video information
    with open(output_file, 'w', encoding='utf-8') as file:
        for video in results:
            #print('\n\n\n',video)
            video_info = {
                'title': video.get('title', ''),
                'description': video.get('descriptionSnippet', [{'text': ''}])[0]['text'],
                'views': video.get('viewCount', ''),
                'upload_date': video.get('publishedTime', ''),
                'link': video.get('link', ''),
                'thumbnail_url': video.get('thumbnails', [])[0].get('url', '')
            }

            # Save the output to a file
            file.write(f"Title: {video_info['title']}_placeholder_\n")
            file.write(f"Description: {video_info['description']}_placeholder_\n")
            file.write(f"Views: {video_info['views']}_placeholder_\n")
            file.write(f"Upload Date: {video_info['upload_date']}_placeholder_\n")
            file.write(f"Link: {video_info['link']}_placeholder_\n")
            file.write(f"Thumbnail URL: {video_info['thumbnail_url']}_placeholder_\n")
            file.write("----\n")


def process_channel_url(channel_url):
    # Check if the input starts with the valid base URL
    if channel_url.startswith("https://www.youtube.com/"):
        # Extract the channel name from the URL
        if "/c/" in channel_url or "/channel/" in channel_url:
            # If the link is already in the desired format, return as is
            return channel_url
        else:
            # Extract the channel name from the URL
            channel_name = channel_url.split("youtube.com/")[-1]

            # Remove any additional parameters in the URL
            channel_name = channel_name.split("?")[0]

            # Create the formatted channel link
            formatted_channel_url = f"https://www.youtube.com/c/{channel_name}"

            return formatted_channel_url

    return None


def display_channel_info():
    # Read the saved output file and display the information
    with open("output.txt", "r", encoding="utf-8") as file:
        video_info = file.read()

        # Replace placeholder with newline characters
        video_info = video_info.replace("_placeholder_", "\n")

        # Display information with custom font size using st.write
        lines = video_info.split("----\n")[:-1]  # Remove the last empty split
        for line in lines:
            parts = line.split(": ", 1)
            if len(parts) == 2:
                key, value = parts
                # Check if the value is a link and format accordingly
                if key.lower() == 'link':
                    st.write(f"**{key}:** [{value}]({value})")
                else:
                    st.write(f"**{key}:** {value}")
                if "Thumbnail URL:" in line:
                    thumbnail_url = line.split("Thumbnail URL: ")[1].strip()
                    st.image(thumbnail_url, caption="Thumbnail", use_container_width=True)
            st.write("-------------\n")




def youtube():
    st.write("Video Search")
    
    init_user_session_state()
    if 'current_youtube_search' not in st.session_state or not st.session_state['current_youtube_search']:
        st.session_state['current_youtube_search'] = 'hamster book stories'
        st.session_state['max_results'] = 10
    
    youtube_search = st.session_state['current_youtube_search']
    max_results = st.session_state['max_results']
    
    final_search = st.text_input("youtube SEARCH", value=youtube_search)

    search_results = search_youtube(search_query=final_search, max_results=max_results)

    for i, result in enumerate(search_results):
        st.header(result["title"])
        thumbnail_url = result['thumbnails'][0].get('url')
        st.image(thumbnail_url, caption="Thumbnail", use_container_width=False)
        # st.image(result["thumbnails"][0], caption="Thumbnail", use_container_width=True)
        st.markdown("**Duration:** " + str(result['duration']) + " | **Views:** " + str(result['views']))
        st.markdown("**Link:** [" + result['link'] + "](" + result['link'] + ")")
        # st.button(f"{result['title']},", key=result['title'])
        button_key = f"play_button_{i}"
        if st.button(f"Play Video {result['title']}", key=button_key):
            st.video(result['link']) 
    
        st.write("---")  # Separator between results
    
    channel_url = st.text_input("Enter the YouTube channel link:")

    if st.button("Get Channel Videos Info"):
        # Process the input link
        formatted_channel_url = process_channel_url(channel_url)

        # Validate the input
        if not formatted_channel_url:
            st.error("Please enter a valid YouTube channel link.")
        else:
            # Call the function to get and display channel videos info
            get_channel_videos_info(formatted_channel_url)
            display_channel_info()


if __name__ == "__main__":

    authenticator = all_page_auth_signin().get('authenticator')
    tabs = st.tabs(["Translate", 'Search Youtube'])
    constants = init_constants()
    OZZ_DB = constants.get('OZZ_DB')
    translate_file = os.path.join(OZZ_DB, 'translate_history.json')
    if os.path.exists(translate_file) == False:
        save_json(translate_file, {})

    translate_history = load_local_json(translate_file)

    with tabs[1]:
        youtube()


    from youtubesearchpython import VideosSearch
    import yt_dlp
    import whisper
    import os
    import subprocess
    import tempfile

    def download_youtube_audio(url, output_dir):
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            audio_path = os.path.splitext(filename)[0] + ".mp3"
            return audio_path

    def transcribe_and_translate(audio_path, model_size="base"):
        model = whisper.load_model(model_size)
        result = model.transcribe(audio_path, task="translate")
        return result["text"]

    def youtube_to_english_transcript(url):
        with tempfile.TemporaryDirectory() as tmpdir:
            print("🔻 Downloading audio...")
            audio_path = download_youtube_audio(url, tmpdir)
            
            print("🧠 Transcribing and translating...")
            transcript = transcribe_and_translate(audio_path)

            print("✅ Done!")
            return transcript
    with tabs[0]:
    # Example
        # url = "https://www.youtube.com/watch?v=SKbmnCfxz6A"
        url = st.text_input("YouTube URL", )
        title=None
        if url:
            url_data = get_youtube_video_metadata(url)
            meta_data = url_data
            title = url_data.get('title')
        if title:
            translate = st.button(f"translate: {title}")
            if url and translate:
                with st.spinner("Translating Youtube Page"):
                    translated_text = youtube_to_english_transcript(url)
                    data_save = {'meta_data': meta_data, 'translated_text': translated_text}

                    translate_history[title] = data_save
                    save_json(translate_file, translate_history)

                st.write("🔊 Transcription:", translated_text)
            
            see_translation = st.selectbox("Tranlations", options=list(translate_history.keys()), key='translation')
            if see_translation:
                st.write(translate_history[see_translation]['translated_text'])

    
    # Split into chunks that don’t exceed a token limit
    def chunk_text(text, max_words_per_chunk=3000):
        words = text.split()
        chunks = []

        for i in range(0, len(words), max_words_per_chunk):
            chunk = " ".join(words[i:i + max_words_per_chunk])
            chunks.append(chunk)

        return chunks

    # Wrapper for summarizing large text
    def summarize_large_text(long_text):
        chunks = chunk_text(long_text)
        summaries = []

        for i, chunk in enumerate(chunks):
            print(f"Summarizing chunk {i+1}/{len(chunks)}")
            history = [
                {"role": "system", "content": "Summarize the following text clearly and concisely."},
                {"role": "user", "content": chunk}
            ]
            summary = llm_assistant_response(history)
            summaries.append(summary)

        combined_summary_prompt = "\n\n".join(summaries)
        final_summary_history = [
            {"role": "system", "content": "Summarize the following multiple section summaries into one cohesive final summary."},
            {"role": "user", "content": combined_summary_prompt}
        ]
        return llm_assistant_response(final_summary_history)
    
    if st.session_state.get('translation'):
        if st.button("Summarizes"):
            data = summarize_large_text(translate_history[see_translation].get('translated_text'))

            st.write(data)

















# from deep_translator import GoogleTranslator
# import re
# sentences = re.split(r'(?<=[.!?]) +', russian_text)
# translated_sentences = [GoogleTranslator(source='auto', target='en').translate(sentence) for sentence in sentences]

# # Join back into a single string
# translated_text = " ".join(translated_sentences)
# print(translated_text)