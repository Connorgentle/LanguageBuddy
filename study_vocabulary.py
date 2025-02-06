import streamlit as st
import pandas as pd
from reverso_context_api import Client
from gtts import gTTS
import io
import random
from firebase_admin import firestore  # Now needed for updates

def fetch_vocabulary_once(user_id, lang_pair, db):
    words_collection = db.collection('users').document(user_id).collection('vocabulary').document(lang_pair).collection('words')
    vocab = [{'Word': doc.id, 'Fluency': doc.to_dict().get('fluency', 'new')} for doc in words_collection.stream()]
    return pd.DataFrame(vocab)

def display_vocabulary():
    if 'username' not in st.session_state or not st.session_state.username:
        st.error("Please log in to view your vocabulary.")
        return

    native_language = st.session_state.get("native_language", "en")
    target_language = st.session_state.get("target_language", "fr")
    lang_pair = f"{native_language}-{target_language}"

    if 'vocabulary_df' not in st.session_state:
        st.session_state.vocabulary_df = fetch_vocabulary_once(st.session_state.username, lang_pair, st.session_state.db)

    if st.session_state.vocabulary_df.empty:
        st.write("Your vocabulary list is empty. Start learning new words!")
    else:
        with st.expander(f"View your {native_language}-{target_language} Vocabulary (you can download this as a csv by hovering over the table then clicking the download icon in the top right)"):
            st.dataframe(st.session_state.vocabulary_df, use_container_width=True)
        with st.expander("Flashcard instructions"):
            st.text("Select the fluency level of words you would like to study. If you are just starting on LanguageBuddy, this will be '1 - new'. Click Begin Flashcard Session and 10 flashcards will be generated below from randomly selected words in your vocabulary of that fluency type. You can practice your pronunciation by listening to the audio clip. When you want to see the answer, hit Show translation. To update the fluency level for the word, select one of the radio buttons. After the last flashcard, you will see an Update Fluency button. Press it to update your personal vocabulary list in the cloud. (note this will not update the dataset shown above, only your data in the cloud.)")

@st.cache_data
def get_translation(text):
    native_language=st.session_state.get("native_language","en")
    target_language=st.session_state.get("target_language")
    client = Client(target_language, native_language)
    return list(client.get_translations(text))

@st.cache_data
# def get_pronunciation(word, language=st.session_state.get("target_language", "fr")):
def get_pronunciation(word):
    language=st.session_state.get("target_language")
    tts = gTTS(text=word, lang=language, slow=False)
    audio_bytes = io.BytesIO()
    tts.write_to_fp(audio_bytes)
    audio_bytes.seek(0)
    return audio_bytes

def update_fluency(word, new_fluency):
    if 'fluency_changes' not in st.session_state:
        st.session_state.fluency_changes = {}
    st.session_state.fluency_changes[word] = new_fluency

def app():
    if 'db' not in st.session_state:
        st.session_state.db = firestore.client()
    
    display_vocabulary()
    
    fluency_levels = ["new", "unfamiliar", "familiar", "learned", "known"]

    # Flashcard Session Start
    st.subheader(":orange[Flashcard Session]")
    selected_fluency = st.selectbox("Select Fluency Level:", fluency_levels, index=0)
    start = st.button("Begin Flashcard Session")

    if 'flashcards' not in st.session_state:
        st.session_state.flashcards = []
    
    if start:
        st.session_state.flashcards = []
        st.session_state.fluency_changes = {}
        
        filtered_vocab = st.session_state.vocabulary_df[st.session_state.vocabulary_df['Fluency'] == selected_fluency]
        if filtered_vocab.empty:
            st.write(f"No words at the '{selected_fluency}' fluency level.")
        else:
            words_to_show = filtered_vocab.sample(min(10, len(filtered_vocab)))  # Randomly select up to 10 words
            st.session_state.flashcards = words_to_show.to_dict('records')

 # Show flashcards only if they have been selected
    if st.session_state.flashcards:
        for i, word in enumerate(st.session_state.flashcards):
            # Use markdown for formatting the title with yellow color and larger font
            st.markdown(f'<p style="color:green; font-size:24px;">Flashcard {i+1}: {word["Word"]}</p>', unsafe_allow_html=True)
            audio_bytes = get_pronunciation(word['Word'])
            st.audio(audio_bytes.getvalue())
            
            # Use an expander for showing the translation
            with st.expander("Show Translation"):
                translations = get_translation(word['Word'])
                if translations:
                    st.write(f"Translation: {', '.join(translations[:3])}")
                else:
                    st.write(f"No translations found for '{word['Word']}'.")
            
            # Show radio buttons for fluency change from the start
            new_fluency = st.radio("Fluency:", fluency_levels, index=fluency_levels.index(word['Fluency']), key=f"fluency_{i}")
            if new_fluency != word['Fluency']:
                update_fluency(word['Word'], new_fluency)

        if st.session_state.flashcards:
            if st.button("Update Fluency"):
                db = st.session_state.db
                for word, new_fluency in st.session_state.fluency_changes.items():
                    doc_ref = db.collection('users').document(st.session_state.username).collection('vocabulary').document(f"{st.session_state.get('native_language', 'en')}-{st.session_state.get('target_language', 'fr')}").collection('words').document(word)
                    doc_ref.update({'fluency': new_fluency})
                st.success("Fluency levels updated successfully!")
