import streamlit as st

from streamlit_option_menu import option_menu
import os
from dotenv import load_dotenv
load_dotenv()

import account, learn, progress, study_vocabulary, about
st.set_page_config(
        page_title="Language Buddy",
)


st.markdown(
    """
        <!-- Global site tag (gtag.js) - Google Analytics -->
        <script async src=f"https://www.googletagmanager.com/gtag/js?id={os.getenv('analytics_tag')}"></script>
        <script>
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', os.getenv('analytics_tag'));
        </script>
    """, unsafe_allow_html=True)
print(os.getenv('analytics_tag'))


class MultiApp:

    def __init__(self):
        self.apps = []

    def add_app(self, title, func):
        self.apps.append({
            "title": title,
            "function": func
        })

    def run():
        # Check if user is logged in before showing the sidebar menu
        if 'username' not in st.session_state or st.session_state.username == '':
            account.app()  # Directly go to account page if not logged in
            return  # This will stop the function here if not logged in

        with st.sidebar:        
            app = option_menu(
                menu_title='LanguageBuddy ',
                options=['Account','Learn','Study Vocabulary','Your Progress','about'],
                icons=['person-circle','caret-right-square-fill','book','graph-up','info-circle-fill'], 
                menu_icon='people-fill', 
                default_index=0,  # Changed to 0 to default to Account when logged in
                styles={
                    "container": {"padding": "5!important","background-color":'black'},
                    "icon": {"color": "white", "font-size": "23px"}, 
                    "nav-link": {"color":"white","font-size": "20px", "text-align": "left", "margin":"0px", "--hover-color": "blue"},
                    "nav-link-selected": {"background-color": "#02ab21"},
                }
            )

        if app == "Account":
            account.app()  
        if app == "Learn":
            learn.app()
        if app == "Your Progress":
            progress.app()        
        if app == 'Study Vocabulary':
            study_vocabulary.app()
        if app == 'about':
            about.app()      

    run()