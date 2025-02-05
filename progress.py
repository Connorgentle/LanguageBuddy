import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from firebase_admin import firestore

def fetch_vocabulary_stats(user_id, lang_pair, db):
    words_collection = db.collection('users').document(user_id).collection('vocabulary').document(lang_pair).collection('words')
    vocab = [{'Word': doc.id, 'Fluency': doc.to_dict().get('fluency', 'new')} for doc in words_collection.stream()]
    df = pd.DataFrame(vocab)
    
    stats = df['Fluency'].value_counts().reindex(['new', 'unfamiliar', 'familiar', 'learned', 'known']).dropna()
    stats = stats[stats > 0].reset_index()
    stats.columns = ['Fluency', 'Count']
    return stats

def plot_fluency_stats(stats):
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = ['#FF6347', '#4682B4', '#9ACD32', '#FFD700', '#8B4513']
    cmap = ListedColormap(colors)
    
    bars = ax.bar(stats['Fluency'], stats['Count'], color=cmap(range(len(stats))))
    
    # Add labels on top of each bar, formatted as integers
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',  # Convert to integer for display
                ha='center', va='bottom', color='black')

    ax.get_yaxis().set_ticks([])
    
    ax.set_xlabel('Fluency Level', color='black')
    ax.set_ylabel('')
    ax.set_title('Vocabulary by Fluency Level', color='black')
    
    fig.patch.set_facecolor('#D3D3D3')
    ax.set_facecolor('#D3D3D3')
    
    for spine in ax.spines.values():
        spine.set_edgecolor('black')

    plt.tight_layout()
    
    st.pyplot(fig)

def app():
    if 'db' not in st.session_state:
        st.session_state.db = firestore.client()
    
    if 'username' not in st.session_state or not st.session_state.username:
        st.error("Please log in to view statistics.")
        return

    native_language = st.session_state.get("native_language", "en")
    target_language = st.session_state.get("target_language", "fr")
    lang_pair = f"{native_language}-{target_language}"

    stats = fetch_vocabulary_stats(st.session_state.username, lang_pair, st.session_state.db)
    
    if not stats.empty:
        plot_fluency_stats(stats)
    else:
        st.write("No vocabulary data available for statistics.")