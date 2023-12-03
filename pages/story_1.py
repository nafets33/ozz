from youtubesearchpython import ChannelsSearch
from youtubesearchpython import *
import streamlit as st
import os




# These are the formats supported in Streamlit right now.
VIDEO_EXTENSIONS = ["mp4", "ogv", "m4v", "webm"]

# For sample video files, try the Internet Archive, or download a few samples here:
# http://techslides.com/sample-webm-ogg-and-mp4-video-files-for-html5


st.title("Video Widget Examples")

st.header("Local video files")
st.write(
    "You can use st.video to play a locally-stored video by supplying it with a valid filesystem path."
)

def get_video_files_in_dir(directory):
    out = []
    for item in os.listdir(directory):
        try:
            name, ext = item.split(".")
        except:
            continue
        if name and ext:
            if ext in VIDEO_EXTENSIONS:
                out.append(item)
    return out


avdir = os.path.expanduser("~")
files = get_video_files_in_dir(avdir)

if len(files) == 0:
    st.write(
        "Put some video files in your home directory (%s) to activate this player."
        % avdir
    )

else:
    filename = st.selectbox(
        "Select a video file from your home directory (%s) to play" % avdir,
        files,
        0,
    )

    st.video(os.path.join(avdir, filename))
st.header("Remote video playback")
st.write("st.video allows a variety of HTML5 supported video links, including YouTube.")


def shorten_vid_option(opt):
    return opt.split("/")[-1]


# A random sampling of videos found around the web.  We should replace
# these with those sourced from the streamlit community if possible!
vidurl = st.selectbox(
    "Pick a video to play",
    (
        "https://youtu.be/_T8LGqJtuGc",
        "https://www.youtube.com/watch?v=kmfC-i9WgH0",
        "https://www.youtube.com/embed/sSn4e1lLVpA",
        "http://www.rochikahn.com/video/videos/zapatillas.mp4",
        "http://www.marmosetcare.com/video/in-the-wild/intro.webm",
        "https://www.orthopedicone.com/u/home-vid-4.mp4",
        "https://www.youtube.com/watch?v=8dO2dOLg4qQ",
    ),
    0,
    shorten_vid_option,
)

st.video(vidurl)