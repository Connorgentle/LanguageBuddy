import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import json
import requests
import os


firebase_credentials_json = st.secrets['FIREBASE_CREDENTIALS_PATH']

try:
    # Parse the JSON string into a dictionary
    firebase_credentials_dict = json.loads(firebase_credentials_json)
    # Pass the dictionary directly to Certificate
    cred = credentials.Certificate(firebase_credentials_dict)
    firebase_admin.initialize_app(cred)
except json.JSONDecodeError:
    raise EnvironmentError("Invalid JSON format for Firebase credentials.")
except KeyError:
    raise EnvironmentError("Firebase credentials not set in Streamlit secrets.")
except Exception as e:
    raise EnvironmentError(f"Error initializing Firebase: {str(e)}")

# Initialize Firestore client
db = firestore.client()

def app():
    st.title('Welcome to :orange[LanguageBuddy] :sunglasses:')

    if 'username' not in st.session_state:
        st.session_state.username = ''
    if 'useremail' not in st.session_state:
        st.session_state.useremail = ''

    def check_username_uniqueness(username):
        """
        Check if a username is unique in the Firestore 'users' collection.
        """
        users_ref = db.collection('users')
        query = users_ref.where('username', '==', username).limit(1)
        results = query.get()
        return len(results) == 0

    def sign_up_with_email_and_password(email, password, username=None, return_secure_token=True):
        if not username:
            return False, "Username is required."

        # Check username uniqueness first
        if not check_username_uniqueness(username):
            return False, "Username already exists."

        try:
            rest_api_url = "https://identitytoolkit.googleapis.com/v1/accounts:signUp"
            payload = {
                "email": email,
                "password": password,
                "returnSecureToken": return_secure_token
            }
            if username:
                payload["displayName"] = username 
            payload = json.dumps(payload)
            r = requests.post(rest_api_url, params={"key": "AIzaSyApr-etDzcGcsVcmaw7R7rPxx3A09as7uw"}, data=payload)
            if r.status_code == 200:
                # Store user in Firestore after successful authentication
                user_data = r.json()
                db.collection('users').document(user_data['localId']).set({
                    'username': username,
                    'email': email,
                    # Add other user details here
                })
                return True, user_data['email']
            else:
                return False, r.json().get('error', {}).get('message')
        except Exception as e:
            return False, f'Signup failed: {str(e)}'

    def sign_in_with_email_and_password(email=None, password=None, return_secure_token=True):
        rest_api_url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"

        try:
            payload = {
                "returnSecureToken": return_secure_token
            }
            if email:
                payload["email"] = email
            if password:
                payload["password"] = password
            payload = json.dumps(payload)
            print('payload sigin',payload)
            r = requests.post(rest_api_url, params={"key": "AIzaSyApr-etDzcGcsVcmaw7R7rPxx3A09as7uw"}, data=payload)
            try:
                data = r.json()
                user_info = {
                    'email': data['email'],
                    'username': data.get('displayName')  # Retrieve username if available
                }
                return user_info
            except:
                st.warning(data)
        except Exception as e:
            st.warning(f'Signin failed: {e}')

    def reset_password(email):
        try:
            rest_api_url = "https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode"
            payload = {
                "email": email,
                "requestType": "PASSWORD_RESET"
            }
            payload = json.dumps(payload)
            r = requests.post(rest_api_url, params={"key": "AIzaSyApr-etDzcGcsVcmaw7R7rPxx3A09as7uw"}, data=payload)
            if r.status_code == 200:
                return True, "Reset email Sent"
            else:
                # Handle error response
                error_message = r.json().get('error', {}).get('message')
                return False, error_message
        except Exception as e:
            return False, str(e)

    def f(): 
        try:
            userinfo = sign_in_with_email_and_password(st.session_state.email_input,st.session_state.password_input)
            st.session_state.username = userinfo['username']
            st.session_state.useremail = userinfo['email']
            global Usernm
            Usernm=(userinfo['username'])
            st.session_state.signedout = True
            st.session_state.signout = True    
        except: 
            st.warning('Login Failed')

    def t():
        st.session_state.signout = False
        st.session_state.signedout = False   
        st.session_state.username = ''

    
    if "signedout" not in st.session_state:
        st.session_state["signedout"] = False
    if 'signout' not in st.session_state:
        st.session_state['signout'] = False    

    if not st.session_state["signedout"]: # only show if the state is False, hence the button has never been clicked
        choice = st.selectbox('Login/Signup',['Login','Sign up'])
        email = st.text_input('Email Address')
        password = st.text_input('Password',type='password')
        #adding functionality for other languages (English, Spanish, French, German, Italian. these are the most popular languages supported by youtube transcripts)
        st.markdown("""
        Please select your **Native Language** and your **Target Language** for the learning session:

        - **en** (English)
        - **fr** (French)
        - **es** (Spanish)
        - **de** (German)
        - **it** (Italian)
        """)
        native_language = st.selectbox("Please select your native language.", ("en","fr","es","de","it"))
        target_language = st.selectbox("Please select the target language you would like to learn. ", ("fr","en","es","de","it"))
        st.session_state.email_input = email
        st.session_state.password_input = password
        #store this in session state
        st.session_state.native_language = native_language
        st.session_state.target_language = target_language

        if choice == 'Sign up':
            username = st.text_input("Enter your unique username")
            if st.button('Create my account'):
                success, message = sign_up_with_email_and_password(email=email, password=password, username=username)
                if success:
                    st.success('Account created successfully!')
                    st.markdown('Please Login using your email and password')
                    st.balloons()
                else:
                    st.error(f'Account creation failed: {message}')

    if st.session_state.signout:
        st.subheader(":green[Click on Learn to get started!]")
        st.text('Name '+st.session_state.username)
        st.text('Email id: '+st.session_state.useremail)
        st.text('Native Language: '+st.session_state.get('native_language'))
        st.text('Target Language: '+st.session_state.get('target_language'))
        st.button('Sign out', on_click=t) 
                

