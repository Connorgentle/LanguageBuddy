import streamlit as st
from firebase_admin import firestore
from streamlit_player import st_player
import requests
import xml.etree.ElementTree as ET
import re
from reverso_context_api import Client
from collections import namedtuple

########################################
#     Importing libraries              #
########################################

###################################
# Functions                 #
###################################


def get_transcription(youtube_url: str):
    """
    Extracts the transcription of a YouTube video using direct HTTP requests.

    :param youtube_url: A string representing the URL of the YouTube video.
    :return: A list of dictionaries containing 'text', 'start', and 'duration' keys for the video's transcript.
    :raises Exception: If the transcript for the specified language is not available or if XML parsing fails.
    """
    target_language = st.session_state.get("target_language")
    if not target_language:
        raise Exception("Target language is not set in session state.")

    youtube_id = youtube_url[youtube_url.find("watch?v=")+len("watch?v="):]
    url = f"http://video.google.com/timedtext?lang={target_language}&v={youtube_id}"
    
    response = requests.get(url)
    if response.status_code == 200:
        # Print or log the response content for debugging
        print(f"Response content: {response.text[:1000]}...")  # Print first 1000 chars
        
        try:
            root = ET.fromstring(response.text)
            transcript = []
            for child in root:
                if child.tag == 'text':
                    start = float(child.attrib.get('start', '0'))
                    duration = float(child.attrib.get('dur', '0'))
                    text = child.text or ""
                    text = re.sub(r'\s+', ' ', text).strip()
                    
                    transcript.append({
                        'text': text,
                        'start': start,
                        'duration': duration
                    })
            return transcript
        except ET.ParseError as e:
            raise Exception(f"XML Parsing Error: {str(e)}")
    else:
        raise Exception(f"Could not retrieve a transcript for the video in {target_language}: Status code {response.status_code}")

def remove_punctuation(input_string):
    """
    Remove punctuation from the input string, converting it to lowercase.

    :param input_string: A string from which to remove punctuation.
    :return: A string with punctuation removed and converted to lowercase.
    """
    return re.sub(r'\W+', '', input_string).lower()

@st.cache_data
def get_translation(text, native_language=st.session_state.get("native_language","en"), target_language=st.session_state.get("target_language", "fr")):
    """
    Retrieve translations for a given text using the Reverso Context API.

    :param text: The word or phrase to translate.
    :param native_language: The source language code (default is 'en' for English).
    :param target_language: The target language code for translation (default is 'fr' for French).
    :return: A list of translation strings for the input text.
    """
    client = Client(target_language, native_language)
    return list(client.get_translations(text))

@st.cache_data 
def import_lesson(youtube_url: str):
    """
    Extracts the transcription from a YouTube video URL and returns it.

    :param youtube_url: A string representing the URL of the YouTube video.
    :return: The transcript of the video as returned by `get_transcription`.
    """
    transcript = get_transcription(youtube_url) 
    return transcript

def try_site(url):
    """
    Check if the provided URL exists by attempting to access it.

    :param url: A string representing the URL to check, typically for a YouTube video.
    :return: Boolean, True if the URL returns a 200 status code, False otherwise.
    """
    request = requests.get(url, allow_redirects=False)
    return request.status_code == 200

def send_unique_words_to_firestore(unique_words, user_id, db, lang_pair):
    """
    Send unique words to Firestore, creating or updating them in a subcollection based on language pair.

    :param unique_words: An iterable of unique words to add or update in Firestore.
    :param user_id: The ID of the user whose vocabulary is being updated.
    :param db: A Firestore client instance.
    :param lang_pair: String representing the language pair, e.g., "en-fr".
    :return: None. Updates Firestore in-place.
    """
    words_collection = db.collection('users').document(user_id).collection('vocabulary').document(lang_pair).collection('words')
    
    batch = db.batch()
    
    try:
        for word in unique_words:
            if isinstance(word, str) and word.strip():
                doc_ref = words_collection.document(word)
                batch.set(doc_ref, {"fluency": "1-new"}, merge=True)
        
        batch.commit()
    except Exception as e:
        st.text(f"An error occurred while updating Firestore: {str(e)}")

def update_word_fluency(user_id, word, new_fluency, db):
    """
    Update the fluency level of a specific word in the user's vocabulary stored in Firestore.

    :param user_id: The ID of the user whose vocabulary will be updated.
    :param word: The word whose fluency level needs to be updated.
    :param new_fluency: The new fluency level to set ('new', 'familiar', or 'known').
    :param db: A Firestore client instance used for database operations.
    :raises ValueError: If `new_fluency` is not one of the allowed values.
    :return: None. This function updates Firestore in-place.
    """
    if new_fluency not in ["1-new", "2-recognized", "3-familiar", "4-learned", "5-known"]:
        raise ValueError("Fluency must be '1-new', '2-recognized', '3-familiar', '4-learned', or '5-known'")
    
    user_vocabulary_ref = db.collection('users').document(user_id).collection('vocabulary').document('unique_words')
    user_vocabulary_ref.update({
        f"words.{word}.fluency": new_fluency
    })

@st.cache_data
def batch_get_translations(words, native_language=st.session_state.get("native_language", "en"), target_language=st.session_state.get("target_language", "fr")):
    """
    Batch translate a set of words from one language to another using Reverso Context API.

    :param words: An iterable of words to translate.
    :param native_language: The source language code (default is 'en' for English).
    :param target_language: The target language code for translation (default is 'fr' for French).
    :return: A dictionary where keys are the words from the input and values are lists of translations.
    """
    client = Client(target_language, native_language)
    return {word: list(client.get_translations(word)) for word in words}

def remove_punctuation(input_string):
    """
    Remove punctuation from the input string except for apostrophes, converting it to lowercase.

    :param input_string: A string from which to remove punctuation.
    :return: A string with most punctuation removed but apostrophes kept, converted to lowercase.
    """
    return re.sub(r'[^\w\s\']+', '', input_string).lower()

def process_transcript(transcript, db):
    try:
        unique_words = set()
        for line in transcript:
            if line["text"] != '[Music]':
                # Keep words with apostrophes intact
                cleaned_words = [remove_punctuation(word).lower() for word in line["text"].split() 
                                 if isinstance(word, str) and word.strip() != '']
                unique_words.update(cleaned_words)
        
        native_language = st.session_state.get("native_language", "en")
        target_language = st.session_state.get("target_language", "fr")
        
        if st.session_state.get('username'):
            lang_pair = f"{native_language}-{target_language}"
            send_unique_words_to_firestore(unique_words, st.session_state.username, db, lang_pair)
        
        translations = batch_get_translations([word for word in unique_words if isinstance(word, str) and word], 
                                              native_language, target_language)
        
        html_output = []
        for line in transcript:
            if line["text"] != '[Music]':
                words_with_tooltips = []
                for word in line["text"].split():
                    # Clean the word for translation but keep the original for display
                    cleaned_word = remove_punctuation(word)
                    if cleaned_word and isinstance(cleaned_word, str):
                        # Use the cleaned word for translation lookup but display the original word
                        translation = translations.get(cleaned_word, [])[:3]
                        words_with_tooltips.append(f'<div class="tooltip">{word}<span class="tooltiptext">{", ".join(translation)}</span></div>')
                html_output.append(' '.join(words_with_tooltips))

        return '\n'.join(html_output)

    except Exception as e:
        st.error(f'Error processing script, in process_transcript(): {str(e)}')
        return None

def st_player(youtube_url):
    """
    Display a YouTube video using Streamlit's video component.

    :param youtube_url: A string containing the URL of the YouTube video to be displayed.
    :return: None. This function displays the video directly in the Streamlit app.
    """
    st.video(youtube_url)

def app():
    """
    Main application function for 'LanguageBuddy', a Streamlit app for language learning.

    :return: None. This function controls the flow and display of the Streamlit app.
    """
    st.markdown("""
    <style>
    .tooltip {
      position: relative;
      display: inline-block;
      border-bottom: 1px dotted black;
    }
    .tooltip .tooltiptext {
      visibility: hidden;
      width: 120px;
      background-color: black;
      color: #fff;
      text-align: center;
      border-radius: 6px;
      padding: 5px 0;
      position: absolute;
      z-index: 1;
      bottom: 125%; 
      left: 50%; 
      margin-left: -60px;
      opacity: 0;
      transition: opacity 0.3s;
    }
    .tooltip:hover .tooltiptext {
      visibility: visible;
      opacity: 1;
    }
    .transcript {
      font-size: 24px;
      line-height: 2;
    }
    </style>
    """, unsafe_allow_html=True)

    if 'db' not in st.session_state:
        st.session_state.db = ''

    db = firestore.client()
    st.session_state.db = db

    if st.session_state.username == '':
        st.error("Please log in with a valid username.")
        return  
    else:
        with st.expander(':orange[Expand for Instructions]'):
            st.markdown("""
            In a separate tab of your web browser, open [YouTube](https://www.youtube.com) and find a video to watch. 
            You can use [Google Translate](https://translate.google.com/) to get the search terms that interest you 
            in your target language from your native language. The video should be less than 5 minutes long and have 
            captions in your target language. Use Youtube's Filters -> Duration -> Under 4 minutes.
            Copy the URL for the YouTube video and paste it in the box below, then click the **Import Lesson** button. 
            """)
            st.subheader(":orange[For the best results]")
            
            st.markdown("""
            <ol>
                <li>Pick a video less than 5 minutes long.</li>
                <li>Watch the entire video without subtitles</li>
                <li>Read the transcription and use the mouse to hover over unknown words</li>
                <li>Rewatch the video with subtitles</li>
                <li>Repeat steps 2, 3, and 4 until you understand most of the content</li>
                <li>Commit to doing this exercise at least once a day on LanguageBuddy!</li>
            </ol>
            """, unsafe_allow_html=True)

        youtube_url = st.text_area(
            label=' :orange[Enter the YouTube URL below and click Import Lesson - (video should be less than 5 minutes)]',
            placeholder='Enter YouTube URL',
            height=None, 
            max_chars=500
        )

        if st.button('Import Lesson', use_container_width=True):
            if youtube_url != '':
                if try_site(youtube_url):  
                    try:
                        st_player(youtube_url)
                        transcript = import_lesson(youtube_url)

                        try:
                            formatted_transcript = process_transcript(transcript, db)
                            if formatted_transcript:
                                st.markdown(f"""
                                <div class="transcript">
                                {formatted_transcript}
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                script = []
                                for line in transcript:
                                    text = line["text"]
                                    if text != '[Music]':
                                        script.append(text)
                                st.text('\n\n'.join(script))  
                        except Exception as e:
                            st.error(f'Error processing script, in app(): {str(e)}')
                            script = []
                            for line in transcript:
                                text = line["text"]
                                if text != '[Music]':
                                    script.append(text)
                            st.text('\n\n'.join(script))  
                    except Exception as e:
                        st.error(f'Error processing video: {str(e)}')
                else:
                    st.error('Invalid YouTube URL or video not accessible.')
            else:
                st.warning('Please enter a YouTube URL.')