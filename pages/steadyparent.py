import streamlit as st
import os
import streamlit.components.v1 as components
from PIL import Image
from ozz_auth import all_page_auth_signin, send_email
from master_ozz.utils import init_constants
import pandas as pd

# Authentication
all_page_auth_signin(force_db_root=True)

# Initialize constants
constants = init_constants()
OZZ_db_images = constants['OZZ_db_images']
OZZ_DB = constants['OZZ_DB']
calendly_url = "https://calendly.com/nstapinski/30min"

if not os.path.exists(os.path.join(OZZ_DB, 'SParent.csv')):
    df = pd.DataFrame(columns=["Email"])
    df.to_csv(os.path.join(OZZ_DB, 'SParent.csv'))

SParent = pd.read_csv(os.path.join(OZZ_DB, 'SParent.csv'))

if 'waitlist' in st.query_params:
    df = pd.DataFrame(SParent)
    st.write(df)

def get_theme_colors():
    """Extract colors from Streamlit theme config"""
    try:
        primary = st.get_option("theme.primaryColor") or "#5f7d6bff"
        background = st.get_option("theme.backgroundColor") or "#fef6e4"
        secondary_bg = st.get_option("theme.secondaryBackgroundColor") or "#c9dbcaff"
        text = st.get_option("theme.textColor") or "#485b48ff"
        
        return {
            "primary": primary,
            "background": background,
            "secondary_bg": secondary_bg,
            "text": text
        }
    except:
        # Fallback to your config values if st.get_option fails
        return {
            "primary": "#5f7d6bff",
            "background": "#fef6e4",
            "secondary_bg": "#c9dbcaff",
            "text": "#485b48ff"
        }

# Initialize theme colors
THEME = get_theme_colors()

# ============== ENHANCED STYLING FUNCTIONS ==============

def styled_text(
    text="Hello There",
    align="left",
    color=None,  # Now defaults to None, will use theme
    fontsize=16,
    font=None,  # Now defaults to None, will use theme
    background_color=None,
    padding=None,
    margin=None,
    border=None,
    border_radius=None,
    font_weight="normal",
    line_height=None,
    text_decoration=None,
    hyperlink=False,
    sidebar=False,
    tag="p"
):
    """
    Enhanced markdown text with comprehensive styling options.
    Automatically uses Streamlit theme colors as defaults.
    """
    
    # Use theme colors if not specified
    if color is None:
        color = THEME["text"]
    if font is None:
        font_option = st.get_option("theme.font") or "sans serif"
        font_map = {
            "sans serif": "Arial, Helvetica, sans-serif",
            "serif": "Georgia, Times New Roman, serif",
            "monospace": "Courier New, monospace"
        }
        font = font_map.get(font_option, "Arial, Helvetica, sans-serif")
    
    styles = [
        f"text-align: {align}",
        f"font-family: {font}",
        f"color: {color}",
        f"font-size: {fontsize}px" if isinstance(fontsize, int) else f"font-size: {fontsize}",
        f"font-weight: {font_weight}"
    ]
    
    if background_color:
        styles.append(f"background-color: {background_color}")
    if padding:
        styles.append(f"padding: {padding}")
    if margin:
        styles.append(f"margin: {margin}")
    if border:
        styles.append(f"border: {border}")
    if border_radius:
        styles.append(f"border-radius: {border_radius}")
    if line_height:
        styles.append(f"line-height: {line_height}")
    if text_decoration:
        styles.append(f"text-decoration: {text_decoration}")
    
    style_string = "; ".join(styles)
    
    if hyperlink:
        html = f'<a style="{style_string}; display: block;" href="{hyperlink}">{text}</a>'
    else:
        html = f'<{tag} style="{style_string}">{text}</{tag}>'
    
    if sidebar:
        st.sidebar.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown(html, unsafe_allow_html=True)
    
    return True


def header_text(text, color=None, fontsize=32, align="left", **kwargs):
    """Styled header text - uses theme primary color by default"""
    if color is None:
        color = THEME["primary"]
    return styled_text(text, color=color, fontsize=fontsize, align=align, font_weight="bold", **kwargs)


def subheader_text(text, color=None, fontsize=24, align="left", **kwargs):
    """Styled subheader text - uses theme primary color by default"""
    if color is None:
        color = THEME["primary"]
    return styled_text(text, color=color, fontsize=fontsize, align=align, font_weight="600", **kwargs)


def highlight_text(text, background_color=None, padding="10px 15px", border_radius="5px", **kwargs):
    """Highlighted text - uses theme secondary background by default"""
    if background_color is None:
        background_color = THEME["secondary_bg"]
    return styled_text(text, background_color=background_color, padding=padding, border_radius=border_radius, **kwargs)


def callout_box(text, background_color=None, border=None, padding="15px", border_radius="8px", **kwargs):
    """Callout box - uses theme colors by default"""
    if background_color is None:
        background_color = THEME["secondary_bg"]
    if border is None:
        border = f"2px solid {THEME['primary']}"
    return styled_text(text, background_color=background_color, border=border, padding=padding, border_radius=border_radius, **kwargs)


def emphasis_text(text, color=None, fontsize=18, font_weight="600", **kwargs):
    """Emphasized text - uses theme primary color by default"""
    if color is None:
        color = THEME["primary"]
    return styled_text(text, color=color, fontsize=fontsize, font_weight=font_weight, **kwargs)


def quote_text(text, color=None, fontsize=16, align="center", font_weight="300", line_height="1.6", **kwargs):
    """Quote-style text - uses theme text color by default"""
    if color is None:
        color = THEME["text"]
    return styled_text(
        f'"{text}"', 
        color=color, 
        fontsize=fontsize, 
        align=align, 
        font_weight=font_weight,
        line_height=line_height,
        **kwargs
    )


# Page Header
st.title("Steady the Parent. Protect the Child.")
# st.divider()

st.markdown("### *Steadying parents so children can feel safe through change.*")

styled_text("Put your oxygen mask on first - because your child can't. ⁉️", padding="15px", fontsize=16, font_weight="bold")

# Introduction Section
st.markdown("""
When families go through major transitions, children are affected more deeply than adults, even when they look "fine".

**You can seek support. Your child can't** - they rely on your nervous system to feel safe.

If your family is going through a big change and you're trying to stay calm, present, and emotionally safe for your child - even when everything feels uncertain - **you're in the right place.**
""")

st.markdown("---")

# About Section
st.header("That's where this work begins")

cols = st.columns([3, 2])
with cols[0]:
    st.markdown("""
    I'm **Nadiya Stapinski**, Certified Martha Beck Coach, I work in neuroscience informed attachment based parenting approach. I'm IFS informed coach and Stress Resilience coach with **over 100+ parents supported** through major family transitions — including divorce, grief, and high-conflict co-parenting.
    
    I provide attachment-based support for parents navigating tough family transitions - so children don't carry what even adults were never meant to hold.
    
    **This is not about perfect parenting.**
    **Professionally**, my work is grounded in attachment science, nervous system regulation, Internal Family Systems, somatic practices, art therapy, and trauma-informed care. 

    **Personally**, I was five years old when my parents went through a highly dysfunctional divorce, and I later experienced the loss of my father as a child. I know firsthand how deeply children absorb unspoken stress - and understand how profoundly one emotionally steady adult can change the outcome.

    I help parents steady themselves so their children don't have to - **preserving what matters most: your relationship with your child and your shared emotional safety.**
    
    """)
    styled_text("    It's about nervous system regulation, emotional safety, and preserving attachment during change."
                , fontsize=18, font_weight="600", padding="10px 0")


with cols[1]:
    # Add image if available
    image_path = os.path.join(OZZ_db_images, 'nadiya_sp.jpg')
    if os.path.exists(image_path):
        image = Image.open(image_path)
        st.image(image, width=350, caption="Nadiya Stapinski, M.A., M.A. - Certified Martha Beck Coach & Attachment-Based Parenting Coach")

# CTA Buttons
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    if st.button("👉 Book a free 30-minute consultation", use_container_width=True, type="primary"):
        st.session_state.show_calendly = True
with col2:
    with st.expander("👉 Join the waitlist for Steady Parent Support Circle", False):
        # Show waitlist form if button clicked - COMBINED INPUT & SUBMIT
        st.markdown("---")
        subheader_text("📝 Join the Waitlist for Hard Transitions Support Circle")
        
        callout_box(
            "A small, guided space for parents navigating divorce, separation, loss, or major family restructuring.",
            padding="15px",
            margin="10px 0"
        )
        
        with st.form("waitlist_form", clear_on_submit=True):
            user_email = st.text_input("Your Email Address", placeholder="your.email@example.com")
            user_name = st.text_input("Your Name (Optional)", placeholder="How should I address you?")
            transition_type = st.selectbox(
                "What transition are you going through?",
                ["Select...", "Separation/Divorce", "Death of a Loved One", "Major Move", "Other Family Disruption"]
            )
            
            col_submit, col_back = st.columns([1, 1])
            with col_submit:
                submitted = st.form_submit_button("Join Waitlist", use_container_width=True, type="primary")
            with col_back:
                if st.form_submit_button("← Back", use_container_width=True):
                    st.session_state.show_waitlist = False
                    st.rerun()
            
            if submitted:
                if user_email and "@" in user_email:
                    # Check if email already exists
                    if user_email in SParent['Email'].values:
                        st.warning("📧 This email is already on the waitlist! We'll reach out when we're ready to launch.")
                    else:
                        # Build email message
                        message = f"""
                        New Steady Parent Support Circle Waitlist Sign-up:
                        
                        Email: {user_email}
                        Name: {user_name if user_name else 'Not provided'}
                        Transition: {transition_type if transition_type != 'Select...' else 'Not specified'}
                        """
                        
                        if send_email('steadyparentTM@gmail.com', subject="New Steady Parent Support Circle Waitlist Sign-up", body=message):
                            # Append to CSV
                            new_entry = pd.DataFrame({
                                "Email": [user_email],
                                "Name": [user_name],
                                "Transition": [transition_type],
                                "Date": [pd.Timestamp.now()]
                            })
                            SParent = pd.concat([SParent, new_entry], ignore_index=True)
                            SParent.to_csv(os.path.join(OZZ_DB, 'SParent.csv'), index=False)
                            
                            st.success("✅ Thank you! You've been added to the waitlist. I'll reach out when we're ready to launch.")
                            st.balloons()
                        else:
                            st.error("There was an issue sending the email. Please try again or email directly to steadyparentTM@gmail.com")
                else:
                    st.error("⚠️ Please enter a valid email address.")

# Show Calendly embed if button clicked
if st.session_state.get('show_calendly', False):
    st.markdown("---")
    subheader_text("📅 Book Your Free Consultation")
    components.iframe(
        src=calendly_url,
        height=800,
        width=700,
        scrolling=True
    )
    # if st.button("← Back to Page"):
    #     st.session_state.show_calendly = False
    #     st.rerun()
    # st.stop()


st.markdown("---")

# WHO I SUPPORT Section
st.header("👥 WHO I SUPPORT")

st.markdown("""
I support parents who are:

• Considering or are going through separation or divorce and worried about their child's emotional wellbeing

• Parenting alongside a dysregulated, emotionally unavailable, or substance-using co-parent

• Seeing increased tantrums, regressions, anxiety, or acting out after family changes

• Living in constant tension and trying to "hold it together" for their kids

• Carrying guilt, fear, or second-guessing every parenting decision

• Navigating grief, death of a loved one, major move or other major disruptions to family stability
""")

styled_text("Children don't need painless transitions. They need at least one emotionally steady adult.", 
            fontsize=16, font_weight="bold", padding="10px")

st.markdown("""
Even when families change, secure attachment can remain intact - when parents are supported, regulated, and not carrying it alone.
""")

st.markdown("---")

# MY APPROACH Section
st.header("🌳 MY APPROACH / THE Steady Parent Framework™")

st.markdown("*Grounded in attachment science, nervous system regulation, and trauma-informed care.*")

st.markdown("""
This work integrates:
- Attachment theory & child development
- Nervous system regulation (polyvagal-informed)
- Internal Family Systems (IFS)
- Somatic and body-based practices
- Art therapy and expressive tools
- Non-violent communication principles

**Not quick fixes. Not parenting perfection.**  
Real tools for real life during hard seasons.
""")

st.markdown("---")

# HOW I HELP Section
st.header("🛠️ HOW I HELP (What We Actually Do)")

with st.expander("**1. We start with you**", expanded=True):
    st.markdown("""
    Because a regulated parent is a child's strongest protective factor.
    
    We work on:
    - Understanding your triggers and stress responses (fight / flight / freeze / fawn)
    - Somatic tools to come back to baseline when emotions spike
    - Reducing guilt, anxiety, and decision paralysis
    """)

with st.expander("**2. We translate your child's behavior**"):
    st.markdown("""
    Tantrums, regressions, shutdowns, angry outbursts - these are not failures.
    
    We explore:
    - What your child's nervous system is actually communicating
    - How children mask fear, grief, or anxiety (including psychosomatic signs like bedwetting, tics, stomachaches)
    """)

with st.expander("**3. We build emotional safety — even when the co-parent can't or won't**"):
    st.markdown("""
    We focus on:
    - What you can control when the other parent is inconsistent or unsafe
    - Non-verbal communication children absorb (tone, facial expression, body language)
    """)

with st.expander("**4. We create structure that calms the nervous system**"):
    st.markdown("""
    Key elements:
    - Predictability, routines, and agreements
    - Clear but kind boundaries
    - Temporary priority shifts in the time of instability
    """)

with st.expander("**5. We teach emotional literacy and regulation**"):
    st.markdown("""
    For you and your child:
    - Using art, play, movement, and body-based tools to release stored stress
    - Moving from emotional overwhelm into parasympathetic regulation
    """)

st.markdown("---")

# ABOUT ME Section



st.markdown("---")

# FAQs Section
st.header("❓ FAQs")

with st.expander("**Is this appropriate if the other parent isn't cooperative?**"):
    st.markdown("""
    ✔️ **Yes.** Much of this work focuses on what you can control to protect attachment and emotional safety.
    """)

with st.expander("**Do you work alongside therapists/psychiatrists or attorneys?**"):
    st.markdown("""
    ✔️ **Yes.** Many clients are simultaneously working with therapists, psychiatric care, mediators, or divorce attorneys. This work complements those supports by focusing on emotional regulation and child protection.
    """)

with st.expander("**Do you work with parents before divorce decisions are final?**"):
    st.markdown("""
    ✔️ **Absolutely.** Early support often prevents greater emotional fallout for children.
    """)

st.markdown("---")

# SUPPORT OPTIONS Section
st.header("💚 Let me give you support you and your child needs")

st.markdown("**You don't have to do this alone — and your child shouldn't have to absorb it.**")

st.subheader("🌱 Single Session - Stabilization & Clarity")
st.markdown("""
• For immediate support, decision overwhelm, or acute stress  
• Nervous system grounding  
• Clear next steps  
• Child-focused guidance for the moment you're in
""")

st.subheader("🌿 6-Session Support — Steadying Through Transition")
st.markdown("""
For parents actively navigating separation, divorce, grief, or major change.

**Includes:**
- Ongoing attachment-based guidance
- Nervous system regulation tools
- Support between sessions via text/email
- Help responding to real-time parenting challenges
""")

st.subheader("🌳 12-Session Support — Deep Stabilization & Rebuilding")
st.markdown("""
For longer transitions or complex co-parenting dynamics.

**Focuses on:**
- Long-term emotional safety for your child
- Reducing reactivity and chronic stress
- Rebuilding trust, predictability, and connection
- Supporting your healing so patterns don't repeat
""")

st.info("**Investment varies depending on level of support.** Options are discussed during the free consultation.")

st.markdown("---")

# SUPPORT CIRCLE Section
st.header("🔄 HARD TRANSITIONS SUPPORT CIRCLE (Waitlist)")

st.markdown("### *Coming Soon: Online Support Circle for Parents in Transition*")

st.markdown("""
A small, guided space for parents navigating:
- Divorce or separation
- Loss or grief
- Major family restructuring

**Not venting. Not guilting.**

A regulated, facilitated space focused on stabilization, nervous system safety, and attachment.

If interested in joining the Waitlist, shoot me a quick email with your name and the transition you are going through (separation / divorce / death of a loved one / big move etc.) - and I'll get back to you when we are ready.
""")

st.markdown("**Stay tuned!**")

st.markdown("---")

# Footer Section
st.markdown("### 📬 Contact & Connect")

col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    **Email:** steadyparentTM@gmail.com

    📺 [YouTube Channel](https://www.youtube.com/channel/UCK1TLaMhgqKUWDabW1JmmrA)  
    📸 [Instagram](https://www.instagram.com/zenfullmama/)  
    🎵 [TikTok](https://www.tiktok.com/@zenfull_mama)

    """)

with col2:
    st.markdown("""
    ---
    *© 2026 Nadiya Stapinski, M.A., M.A.*
    """)

# Final CTA
st.markdown("---")
st.markdown("### Ready to take the first step?")
if st.button("📅 Book Your Free 30-Minute Consultation", use_container_width=True, type="primary"):
    components.iframe(
        src=calendly_url,
        height=800,
        width=700,
        scrolling=True
    )