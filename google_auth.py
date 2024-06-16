import streamlit as st
import requests
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
import webbrowser
from master_ozz.utils import ozz_master_root
import os

from dotenv import load_dotenv
main_root = ozz_master_root()  # os.getcwd()
load_dotenv(os.path.join(main_root, ".env"))

CLIENT_ID = os.environ.get('google_client_id')
CLIENT_SECRET = os.environ.get('google_secret_id')
REDIRECT_URI = 'http://localhost:8501/'
SCOPES = ['https://www.googleapis.com/auth/userinfo.profile']
def create_flow():
    return Flow.from_client_config(
        client_config={
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://accounts.google.com/o/oauth2/token"
            }
        },
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

# # Create the OAuth flow object
# flow = InstalledAppFlow.from_client_secrets_file(
#     CLIENT_SECRET_FILE, scopes=SCOPES, state=session['state'])
# flow.redirect_uri = url_for('callback', _external=True)

# # Exchange the authorization code for an access token
# authorization_response = request.url
# flow.fetch_token(authorization_response=authorization_response)

# # Save the credentials to the session
# credentials = flow.credentials
# session['credentials'] = credentials_to_dict(credentials)

def main():
    st.title("Google OAuth with Streamlit")
    if 'credentials' not in st.session_state:
        print("1")
        st.session_state['credentials'] = None
    flow = create_flow()
    try:
        if st.button("Sign in with Google"):
            print("2")
            st.write('Opening the authorization page...')
            auth_url, qq = flow.authorization_url(prompt='consent')
            # authorization_response = request.url
            print("qq", qq)
            print("auth_url", auth_url)
            st.empty()
            webbrowser.open(auth_url, new=2)
            # pydeck_chart = st.pydeck_chart()
            # auth_code = pydeck_chart.selectbox('Waiting for authorization code...', options=[None])
            flow.fetch_token(authorization_response=auth_url)
            auth_code = st.text_input('Enter authorization code:', key='auth_code')

            print("3")
            # flow.fetch_token(code=auth_code)
            st.session_state['credentials'] = flow.credentials
            st.success('Authentication successful! You can close this window and return to the Streamlit app.')
            print("4")
            credentials = st.session_state['credentials']
            session = requests.session()
            session.headers.update({'Authorization': f'Bearer {credentials.token}'})
            response = session.get('https://www.googleapis.com/oauth2/v1/userinfo')
            user_info = response.json()
            st.write("User Email:", user_info.get('email'))
    except Exception as e:
        print(f"Error processing: {e}")
if __name__ == "__main__":
    main()


            # from urllib.parse import urlparse, parse_qs
            # print("url", auth_url)
            # url = auth_url

            # # Parse the URL
            # parsed_url = urlparse(url)

            # # Extract query parameters
            # query_params = parse_qs(parsed_url.query)

            # # Get the authorization code
            # print(query_params)
            # authorization_code = query_params.get("client_id", [None])[0]
            # auth_code=authorization_code

            # print("Authorization Code:", authorization_code)
            # print("Received Auth Code:", auth_code)