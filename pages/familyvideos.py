import streamlit as st
import os
from ozz_auth import all_page_auth_signin
from master_ozz.utils import init_constants

CONSTANTS = init_constants()



family_video_dict = {
    'tom carols wedding': 'https://youtu.be/teSnA_wVpDM',
    'kurt claire wedding': 'https://youtu.be/4nW-JTlX-EM',
    'asutria - NH soccer - xmas at kurts - dance': 'https://youtu.be/pB0uDY3qwvU',
    '60s grandma family': 'https://youtu.be/sbu_IUkfsmA',
    '89-90 xmas beach Disney FL': 'https://youtu.be/FpiyQ7Zs1Rg',
    '89 NY clock living at grandpas': 'https://youtu.be/WLaWdS60K_4',
    '89 NY livbday grandpa': 'https://youtu.be/VTuUEDpiL8w',
    '89 90 liv tom NY dancing liv show': 'https://youtu.be/jVmGGtRVCNw',
    '90s FL pool kg NH cabin': 'https://youtu.be/6NDZlycjryY',
    '93 summer liv': 'https://youtu.be/nzSRNEE0XJg',
    'asutria NH soccer xmas at kurts dance': 'https://youtu.be/IqTuomroi2w',
    'Boonie 10 Months': 'https://youtu.be/5bC8rk9LFfU',
    'castle hiking boats dartmouth': 'https://youtu.be/fbMooi0s4mM',
    'christmas olivia': 'https://youtu.be/oJJRYVTcId8',
    'dad boxing kids NY': 'https://youtu.be/nYEfUOiAA14',
    'easter': 'https://youtu.be/KPgPs2uLvXM',
    'French Toast':'https://youtu.be/36mtBruKot8',
    'Austria - Hiking': 'https://youtu.be/oGZs9nT53DQ', 
    'Kids Dancing': 'https://youtu.be/E9w7YylFBU8',
    'Kids Shoveling Snow': 'https://youtu.be/7T_BIQtr7sg',
    'Kids Shoveling Snow 2':'https://youtu.be/PmJAErjRksU',
    'kurt claire wedding FL NH NY': 'https://youtu.be/F04O60mkAKg',
    'kurt clarie wedding': 'https://youtu.be/QtCwGR03DZA',
    'little angles graduation': 'https://youtu.be/ydxVw2_2Ucg',
    'little angels graduation 3': 'https://youtu.be/QMRUOne87iw',
    'little angels graduation 4': 'https://youtu.be/ZBHOWxzy6-s',
    'NH krista hiking FL bday': 'https://youtu.be/VPh7K0Wux7g',
    'NH Tennis BeachBoys FL GrandpaHouse': 'https://youtu.be/Krvm0G3qdZk',
    'Olivia and Jackie': 'https://youtu.be/xzytMtb5J9Y',
    'Olivia Going to School': 'https://youtu.be/9u7jrkrmAvQ',
    'Olivia Sammy dancing': 'https://youtu.be/p5Cx4sPomE0',
    'dad boxing kids NY': 'https://youtu.be/zsN3aGg_Rj4',
    'tennis kurt short shorts': 'https://youtu.be/ymIq4HbRufk',
    'Opa charlie christmas': 'https://youtu.be/P4ZSsZnnqz4',
    'Papa Family reunion': 'https://youtu.be/rHFhuwJ_yyk',
    'Stefan Birthday':'https://youtu.be/UQEOCTYy9P4',
    'Stefan Boon & Manny': 'https://youtu.be/yui37StdOvE',
    'stefan_wants_to_ride_his_bike': 'https://youtu.be/kIZpWHVTP0g',
    'twins birthday Party': 'https://youtu.be/gNMc2g-6s70',
    'xmas babyStefan 3': 'https://youtu.be/12KeUykpbko',
    'xmas_together': 'https://youtu.be/ApjlPLjFVac',

}


def display_family_videos():
    if st.button("Christmas Special! 🎄🎅🎁", use_container_width=True):
        st.snow()
        st.video(family_video_dict['xmas_together'])
        st.write(f'**Link:** [{family_video_dict["xmas_together"]}]({family_video_dict["xmas_together"]})')
        
    
    st.divider()

    cols = st.columns((2,2,2,2))
    with cols[0]:
        st.subheader("Stapinski")
    with cols[2]:
        st.subheader("Grabher")
    with cols[1]:
        img = os.path.join(st.session_state['OZZ_db_images'],'stapinski.jpg')
        if os.path.exists(img):
            st.image(img, width=100)
    with cols[3]:
        img = os.path.join(st.session_state['OZZ_db_images'],'grabher.png')
        if os.path.exists(img):
            st.image(img, width=100)
    st.divider()
    st.subheader("**Family Videos Collection**")
    video_titles = list(family_video_dict.keys())
    selected_video = st.selectbox("Select a specific video:", ["-- Browse all videos --"] + video_titles)

    st.divider()
    
    if selected_video != "-- Browse all videos --":
        # Display selected video
        url = family_video_dict[selected_video]
        st.write(f"**{selected_video}**")
        st.write(f"**Link:** [{url}]({url})")
        st.video(url)
        st.write("-------------")
        return True





    # Initialize session state for pagination
    if 'video_page' not in st.session_state:
        st.session_state.video_page = 0
    
    videos_per_page = 23
    video_list = list(family_video_dict.items())
    total_pages = (len(video_list) + videos_per_page - 1) // videos_per_page
    
    # Get current page videos
    start_idx = st.session_state.video_page * videos_per_page
    end_idx = start_idx + videos_per_page
    current_videos = video_list[start_idx:end_idx]
    
    # Display videos
    for title, url in current_videos:
        # st.write(f"**{title}**")
        st.video(url)
        st.write(f"**Link:** [{url}]({url})")
        st.write("-------------")
    # Pagination buttons
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.session_state.video_page > 0:
            if st.button("← Previous"):
                st.session_state.video_page -= 1
                st.rerun()
    with col2:
        st.write(f"Page {st.session_state.video_page + 1} of {total_pages}")
    with col3:
        if st.session_state.video_page < total_pages - 1:
            if st.button("Next →"):
                st.session_state.video_page += 1
                st.rerun()
                

# Call the function
display_family_videos()