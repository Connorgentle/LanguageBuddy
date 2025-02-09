import streamlit as st
from firebase_admin import firestore
from youtube_transcript_api import YouTubeTranscriptApi
from reverso_context_api import Client
import re

# Assuming these are already set up in session state
native_language = st.session_state.get("native_language", "en")
target_language = st.session_state.get("target_language", "fr")

def get_transcription(youtube_url: str):
    youtube_id = youtube_url[youtube_url.find("watch?v=")+len("watch?v="):]
    transcript = YouTubeTranscriptApi.get_transcript(youtube_id, languages=[target_language])
    return transcript

def remove_punctuation(input_string):
    return re.sub(r'[^\w\s\']+', '', input_string).lower()

@st.cache_data
def batch_get_translations(words, native_language, target_language):
    client = Client(target_language, native_language)
    return {word: list(client.get_translations(word))[:3] for word in words}

def update_user_vocabulary(user_id, words_dict, db):
    user_voc_ref = db.collection('users').document(user_id).collection('vocabulary').document(f"{native_language}-{target_language}")
    batch = db.batch()
    for word, data in words_dict.items():
        doc_ref = user_voc_ref.collection('words').document(word)
        batch.set(doc_ref, data, merge=True)  # merge=True to update existing documents
    batch.commit()

def process_transcript(user_id, youtube_url, db):
    transcript = get_transcription(youtube_url)
    user_vocabulary = import_user_vocabulary(user_id, db)
    unique_words = {}
    
    # Create unique_words dictionary
    for line in transcript:
        if line["text"] != '[Music]':
            for word in remove_punctuation(line["text"]).split():
                if word not in unique_words:
                    unique_words[word] = {'count': 1}
                else:
                    unique_words[word]['count'] += 1

    new_words = {}
    
    # Check if words are in user's vocabulary
    for word, count in unique_words.items():
        if word in user_vocabulary:
            unique_words[word].update({
                'fluency': user_vocabulary[word]['fluency'],
                'translation': user_vocabulary[word]['translation']
            })
        else:
            new_words[word] = {'fluency': "1-new", 'count': count}

    # Batch translation for new words
    if new_words:
        translations = batch_get_translations(new_words.keys(), native_language, target_language)
        for word in new_words:
            new_words[word]['translation'] = translations.get(word, [])
            unique_words[word].update(new_words[word])

    # Update user vocabulary in Firestore
    update_user_vocabulary(user_id, new_words, db)

    # Build transcript with highlighted words and tooltips
    html_output = []
    for line in transcript:
        if line["text"] != '[Music]':
            words_with_tooltips = []
            for word in line["text"].split():
                cleaned_word = remove_punctuation(word)
                if cleaned_word in unique_words:
                    fluency = unique_words[cleaned_word]['fluency']
                    color = {
                        "1-new": "darkblue",
                        "2-recognized": "lightblue",
                        "3-familiar": "yellow",
                        "4-learned": "lightyellow",
                        "5-known": "transparent"
                    }.get(fluency, "transparent")
                    translation = ", ".join(unique_words[cleaned_word].get('translation', []))
                    words_with_tooltips.append(f'<span class="tooltip" style="background-color:{color};">{word}<span class="tooltiptext">{translation}</span></span>')
                else:
                    words_with_tooltips.append(word)  # For words not in unique_words, just display them without color
            html_output.append(' '.join(words_with_tooltips))

    return '\n'.join(html_output)

def import_user_vocabulary(user_id, db):
    user_voc_ref = db.collection('users').document(user_id).collection('vocabulary').document(f"{native_language}-{target_language}")
    words = user_voc_ref.collection('words').stream()
    return {doc.id: doc.to_dict() for doc in words}

def app():
    st.markdown("""
    <style>
    .tooltip {
        position: relative;
        display: inline-block;
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
    </style>
    """, unsafe_allow_html=True)

    db = firestore.client()
    if 'username' not in st.session_state or not st.session_state.username:
        st.error("Please log in with a valid username.")
        return

    youtube_url = st.text_input('Enter YouTube URL:')
    if st.button('Process Video'):
        if youtube_url:
            try:
                html_content = process_transcript(st.session_state.username, youtube_url, db)
                st.markdown(html_content, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
        else:
            st.warning('Please enter a YouTube URL.')