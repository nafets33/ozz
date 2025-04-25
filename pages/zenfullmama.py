import streamlit as st
import os
from bs4 import BeautifulSoup
from ozz_auth import all_page_auth_signin
from master_ozz.utils import init_constants, save_json, init_text_audio_db, ozz_master_root_db, init_user_session_state, hoots_and_hootie_keywords, return_app_ip, ozz_master_root, sign_in_client_user, print_line_of_error, Directory, CreateChunks, CreateEmbeddings, Retriever, init_constants, refreshAsk_kwargs
from streamlit_extras.switch_page_button import switch_page
from dotenv import load_dotenv
from custom_voiceGPT import custom_voiceGPT, VoiceGPT_options_builder
from PIL import Image
import base64

import streamlit as st
import streamlit.components.v1 as components


all_page_auth_signin(force_db_root=True)

calendly_url = "https://calendly.com/stapinski89/30min"  # replace with your actual link
constants = init_constants()
ozz_db = constants['OZZ_DB']
# Embed Calendly using iframe
# about me / Pic
# How we can Book
cols = st.columns((5,2))
with cols[0]:
    st.header("Nadiya Stapinski A Zenfullmama Guide")
    book_s = st.button("Book Your Session Now", use_container_width=True)

if book_s:
    st.title("Book Your First Free Session 📅")
    components.iframe(
        src=calendly_url,
        height=800,
        width=700,
        scrolling=True
    )
    st.stop()

with cols[1]:
    st.markdown("""
    📺 [YouTube Channel](https://www.youtube.com/channel/UCK1TLaMhgqKUWDabW1JmmrA)  
    📸 [Instagram](https://www.instagram.com/zenfullmama/)  
    🎵 [TikTok](https://www.tiktok.com/@zenfull_mama)
    """)
with cols[1]:
    image = Image.open(os.path.join(ozz_db, 'nadiya.png'))
    st.image(image, use_container_width=True)
with cols[0]:
    st.markdown(f"""
                ---
    🌿 **Welcome** to a Calmer, Clearer, More Connected You
    You’re the helper. The peacemaker. The one who always tries to “do the right thing.”
    But inside? You’re exhausted, stretched thin, and wondering: "Why does everything feel so heavy... and still not enough?"
    You're not broken. You're just carrying too much — alone.

    ✨ Coaching for Sensitive Souls, Parents, and People-Pleasers
    Whether you're a parent who wants to break generational patterns, or a deeply feeling adult who struggles with boundaries and self-worth — you're in the right place.
    I help people who are:
    - Constantly putting others first — and losing themselves in the process
    - Living in high-alert mode: anxious, overwhelmed, burned out
    - Saying “yes” when they mean “no” (and resenting it)
    - Stuck in guilt, self-doubt, or fear of conflict
    - Longing to parent with more connection... and less reactivity
    - Healing from complex family dynamics or emotional neglect

          """)

cols = st.columns((5,2))
with cols[1]:
    st.subheader("""💬 **How I Can Help** """)
with cols[0]:
    st.markdown("""
    ---
    I bring together powerful, proven tools to gently untangle the patterns keeping you stuck:
    - Attachment-Based Coaching – understand your emotional blueprint and how it impacts your relationships
    - IFS-Informed Work – meet and heal the “parts” of you that protect, please, or panic
    - Imaginative Rescripting & Inner Child Work – rewrite old emotional scripts
    - Byron Katie’s The Work – question the thoughts that keep you anxious, ashamed, or stuck
    - Martha Beck Wayfinder Coaching – find your truth and your next right step, from the inside out
                """)
cols = st.columns((5,2))
with cols[1]:
    st.subheader("""Real Change Starts Gently""")
with cols[1]:
    image = Image.open(os.path.join(ozz_db, 'mama.jpg'))
    st.image(image, use_container_width=True)
with cols[0]:
    st.markdown("""
    ---
    You don’t need to “fix” yourself — you just need space, support, and safety to soften the old patterns and step into the person (and parent) you already are inside.
    This isn’t therapy. It’s forward-focused, practical, and deeply compassionate work that helps you:
    """ )

    ll = [
    "✅ Set boundaries without guilt",
    "✅ Respond instead of react — especially with your kids",
    "✅ Stop spiraling in your head and start living in your truth",
    "✅ Feel more regulated, present, and self-trusting",
    "✅ Know what you want — and how to ask for it",
    ]
    for i in ll:
        st.markdown(i)

cols = st.columns((1,1))
with cols[0]:
    st.subheader("**First Session Is On Me**")
    st.markdown(f"""
    Let’s talk. No pressure. No performance.
    Just one gentle, grounding session to see how this work feels for you.
    
    👉 [Book Your Free First Session Now]
    Or, if you’re ready for real momentum…
    ✨ **Try a 4-Session Series**
    A focused month of transformation, insight, and tools you’ll use for life.

    💬 **What Clients Say**
    “I didn’t realize how much I was living for everyone else until our first session. I feel like I’ve reclaimed parts of myself I’d forgotten.”
    — Client, mom of two
    “This work changed how I parent, how I talk to my partner, and how I talk to myself.”
    — Client, recovering people-pleaser

    ---
                        
    You’re Not “Too Much.” You’ve Just Been Holding Too Much.
    Let’s unlearn the patterns that kept you small, and rebuild from the inside out.
    You can be soft and strong. You can be kind and have boundaries. You can feel deeply and still feel safe.
    💛 You don’t have to do it alone.
    👉 [Book Your Free Session]
    Or choose a 4-session package to go deeper, faster.
    """)

with cols[1]:
    st.title("Book Your First Free Session 📅")
    components.iframe(
        src=calendly_url,
        height=800,
        width=700,
        scrolling=True
    )