import streamlit as st
from firebase_admin import firestore

########################################
#     Importing libraries              #
########################################

from streamlit_player import st_player
from youtube_transcript_api import YouTubeTranscriptApi
import streamlit as st
import requests
from reverso_context_api import Client
from collections import namedtuple
import re
import streamlit as st

###################################
# Functions                 #
###################################


# def get_transcription(youtube_url: str, target_language = st.session_state.get("target_language")):
def get_transcription(youtube_url: str):
    """
    Extracts the transcription of a YouTube video in the specified target language.

    This function retrieves the video ID from the URL, fetches the transcript, 
    and does not check for existing transcripts in session state as previously 
    described in comments. 

    :param youtube_url: A string representing the URL of the YouTube video.
    :param target_language: The language code for which to fetch the transcript, defaults to 'fr' for French.
    :return: A list of dictionaries, each containing 'text', 'start', and 'duration' keys for the video's transcript.
    """
    #defining target_language here
    target_language = target_language = st.session_state.get("target_language")

    youtube_id = youtube_url[youtube_url.find("watch?v=")+len("watch?v="):]
    transcript = YouTubeTranscriptApi.get_transcript(youtube_id,languages=[target_language])
    return transcript

def remove_punctuation(input_string):
    """
    Remove punctuation from the input string, converting it to lowercase.

    :param input_string: A string from which to remove punctuation.
    :return: A string with punctuation removed and converted to lowercase.
    """
    return re.sub(r'\W+', '', input_string).lower()

#Function to get translations from reverso context (think about replacing/modifying this as it doesnt provide for prronouns and other words)
@st.cache_data
def get_translation(text, native_language=st.session_state.get("native_language","en"), target_language=st.session_state.get("target_language")):
    """
    Retrieve translations for a given text using the Reverso Context API.

    This function initializes a client for the specified languages and 
    returns translations for the provided text.

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

    This function fetches the transcript for educational purposes but does not 
    update any vocabulary base as previously noted. The caching decorator is used 
    to potentially improve performance by storing results of expensive operations.

    :param youtube_url: A string representing the URL of the YouTube video.
    :return: The transcript of the video as returned by `get_transcription`.
    """
    transcript = get_transcription(youtube_url) 
    return transcript

def try_site(url):
    """
    Check if the provided URL exists by attempting to access it.

    This function sends a GET request to the URL without following redirects 
    and checks if the response status code is 200, indicating the URL is accessible.

    :param url: A string representing the URL to check, typically for a YouTube video.
    :return: Boolean, True if the URL returns a 200 status code, False otherwise.
    """
    request = requests.get(url, allow_redirects=False)
    return request.status_code == 200

def send_unique_words_to_firestore(unique_words, user_id, db, lang_pair):
    """
    Send unique words to Firestore, creating or updating them in a subcollection based on language pair.

    This function ensures each word is stored under a specific language pair document, 
    allowing for organized storage by language context.

    :param unique_words: An iterable of unique words to add or update in Firestore.
    :param user_id: The ID of the user whose vocabulary is being updated.
    :param db: A Firestore client instance.
    :param lang_pair: String representing the language pair, e.g., "en-fr".
    :return: None. Updates Firestore in-place.
    """
    # We go directly to the 'words' subcollection under 'vocabulary' for the specific language pair
    words_collection = db.collection('users').document(user_id).collection('vocabulary').document(lang_pair).collection('words')
    
    batch = db.batch()
    
    try:
        for word in unique_words:
            if isinstance(word, str) and word.strip():
                doc_ref = words_collection.document(word)
                batch.set(doc_ref, {"fluency": "new"}, merge=True)
        
        batch.commit()
    except Exception as e:
        # Log or handle the error appropriately
        st.text(f"An error occurred while updating Firestore: {str(e)}")


def update_word_fluency(user_id, word, new_fluency, db):
    """
    Update the fluency level of a specific word in the user's vocabulary stored in Firestore.

    This function checks if the new fluency level is valid before updating 
    the word's fluency in the user's document in Firestore.

    :param user_id: The ID of the user whose vocabulary will be updated.
    :param word: The word whose fluency level needs to be updated.
    :param new_fluency: The new fluency level to set ('new', 'familiar', or 'known').
    :param db: A Firestore client instance used for database operations.
    :raises ValueError: If `new_fluency` is not one of the allowed values.
    :return: None. This function updates Firestore in-place.
    """
    if new_fluency not in ["new", "familiar", "known"]:
        raise ValueError("Fluency must be 'new', 'familiar', or 'known'")
    
    user_vocabulary_ref = db.collection('users').document(user_id).collection('vocabulary').document('unique_words')
    user_vocabulary_ref.update({
        f"words.{word}.fluency": new_fluency
    })


@st.cache_data
# def batch_get_translations(words, native_language="en", target_language="fr"):
#replacing above with new functionality to select languages from drop down
def batch_get_translations(words, native_language=st.session_state.get("native_language"), target_language=st.session_state.get("target_language")):
    """
    Batch translate a set of words from one language to another using Reverso Context API.

    This function creates translations for each word in the input list, 
    caching the results to potentially speed up subsequent calls with the 
    same input.

    :param words: An iterable of words to translate.
    :param native_language: The source language code (default is 'en' for English).
    :param target_language: The target language code for translation (default is 'fr' for French).
    :return: A dictionary where keys are the words from the input and values are lists of translations.
    """
    client = Client(target_language, native_language)
    return {word: list(client.get_translations(word)) for word in words}


def remove_punctuation(input_string):
    """
    Remove all non-word characters from the input string and convert it to lowercase.

    This function uses a regular expression to strip out any character that 
    isn't alphanumeric or underscore, effectively removing punctuation.

    :param input_string: The string to process.
    :return: A new string with all non-word characters removed and converted to lowercase.
    """
    return re.sub(r'\W+', '', input_string).lower()


def process_transcript(transcript, db):
    """
    Process a video transcript to handle unique words, update Firestore with language context, 
    and format text with translation tooltips.

    This function collects unique words from the transcript, sends new words to Firestore 
    based on the language pair, translates these words, and formats the transcript with tooltips.

    :param transcript: A list of dictionaries where each dictionary contains 'text' from the video transcript.
    :param db: A Firestore client instance for database operations.
    :return: A string of HTML formatted text where each word might have a tooltip with translations, or None if an error occurs.
    """
    try:
        unique_words = set()
        for line in transcript:
            if line["text"] != '[Music]':
                cleaned_words = [remove_punctuation(word).lower() for word in line["text"].split() 
                                 if isinstance(word, str) and word.strip() != '']
                unique_words.update(cleaned_words)
        
        # Use session state for language selection
        native_language = st.session_state.get("native_language")
        target_language = st.session_state.get("target_language")
        
        # Send unique words to Firestore, specifying the language pair
        if st.session_state.get('username'):
            lang_pair = f"{native_language}-{target_language}"
            send_unique_words_to_firestore(unique_words, st.session_state.username, db, lang_pair)
        
        # Translate words based on the language pair
        translations = batch_get_translations([word for word in unique_words if isinstance(word, str) and word], 
                                              native_language, target_language)
        
        html_output = []
        for line in transcript:
            if line["text"] != '[Music]':
                words_with_tooltips = []
                for word in line["text"].split():
                    cleaned_word = remove_punctuation(word)
                    if cleaned_word and isinstance(cleaned_word, str):
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

    This function simplifies the process of embedding and showing a YouTube video 
    in a Streamlit application by encapsulating Streamlit's video function.

    :param youtube_url: A string containing the URL of the YouTube video to be displayed.
    :return: None. This function displays the video directly in the Streamlit app.
    """
    st.video(youtube_url)


def app():
    """
    Main application function for 'LanguageBuddy', a Streamlit app for language learning.

    This function sets up the UI, handles user authentication, processes YouTube URLs 
    for educational content, and manages the interaction for importing lessons and 
    displaying video transcripts with translation tooltips.

    - Checks if the user is logged in.
    - Provides an interface for entering a YouTube URL.
    - Manages the process of importing and displaying a lesson from a video by:
      - Validating the URL.
      - Playing the video.
      - Fetching and processing the transcript.
      - Displaying the transcript with translation tooltips.

    :return: None. This function controls the flow and display of the Streamlit app.
    """
    st.markdown("""
    <style>
    .tooltip {
      position: relative;
      display: inline-block;
      border-bottom: 1px dotted black; /* Optional: Indicates it's hoverable */
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
      bottom: 125%; /* Tooltip above the word */
      left: 50%; 
      margin-left: -60px; /* Half of width to center the tooltip */
      opacity: 0;
      transition: opacity 0.3s;
    }

    .tooltip:hover .tooltiptext {
      visibility: visible;
      opacity: 1;
    }
    /* New styles for larger text and increased line spacing */
    .transcript {
      font-size: 24px; /* Double the typical font size */
      line-height: 2; /* Double line height for better readability */
    }
    </style>
    """, unsafe_allow_html=True)

    if 'db' not in st.session_state:
        st.session_state.db = ''

    db=firestore.client()
    st.session_state.db=db

    if st.session_state.username == '':
        st.error("Please log in with a valid username.")
        return  
    else:
        # ... (expander and instructions code remains unchanged)

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
                                # Add a class for styling to the transcript output
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
                                st.text('\n\n'.join(script))  # Double newline for extra space between lines
                        except Exception as e:
                                st.error(f'Error processing script, in app(): {str(e)}')
                                script = []
                                for line in transcript:
                                    text = line["text"]
                                    if text != '[Music]':
                                        script.append(text)
                                st.text('\n\n'.join(script))  # Double newline for extra space between lines
                    except Exception as e:
                        st.error(f'Error processing video: {str(e)}')
                else:
                    st.error('Invalid YouTube URL or video not accessible.')
            else:
                st.warning('Please enter a YouTube URL.')