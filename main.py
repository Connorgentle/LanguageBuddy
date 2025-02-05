import streamlit as st

from streamlit_option_menu import option_menu
import os
from dotenv import load_dotenv
load_dotenv()

import learn, progress, account, study_vocabulary, about, buy_me_a_coffee
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
        # app = st.sidebar(
        with st.sidebar:        
            app = option_menu(
                menu_title='LanguageBuddy ',
                options=['Account','Learn','Study Vocabulary','Your Progress','about'],
                icons=['person-circle','caret-right-square-fill','book','graph-up','info-circle-fill'], #'trophy-fill'
                menu_icon='people-fill', 
                default_index=1,
                styles={
                    "container": {"padding": "5!important","background-color":'black'},
        "icon": {"color": "white", "font-size": "23px"}, 
        "nav-link": {"color":"white","font-size": "20px", "text-align": "left", "margin":"0px", "--hover-color": "blue"},
        "nav-link-selected": {"background-color": "#02ab21"},}
                
                )

        
        if app == "Learn":
            learn.app()
        if app == "Account":
            account.app()    
        if app == "Your Progress":
            progress.app()        
        if app == 'Study Vocabulary':
            study_vocabulary.app()
        if app == 'about':
            about.app()      
             
          
             
    run()            
         
