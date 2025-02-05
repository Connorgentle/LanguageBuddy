import streamlit as st

def app():
    st.title(":orange[About LanguageBuddy]")

    with st.expander("Demystifying Language Learning:"):
        st.markdown("""
        <div class="about-content">
        Have you spent years studying a foreign language only to struggle ordering a coffee? Ever tried watching a movie or TV show in a foreign language, only to turn it off after five minutes, leaving you with nothing but a headache? Have you slaved away doing grammar exercises yet found yourself tongue-tied in basic conversations? Does language learning feel like a long, tortuous journey, with ‘fluency’ seeming like a far-off concept?<br><br>
                    
        Language learning often feels daunting, with fluency seeming out of reach. Conventional methods advocate for learning through rote memorization, worksheets, and flashcards, focusing on grammar and vocabulary from the ground up. But this isn't how we naturally acquire language. Reflect on how you learned your native tongue as a child; it was through observation and play, not grammar lessons.

        Now, let's consider AI and machine learning. Both AI and human babies learn by observing and interacting with vast amounts of data or experiences. An AI doesn't fear mistakes; it learns from them, refining its understanding, much like a child babbling 'goo-goo ga-ga' learns from the feedback it receives. Language isn't just learned; it's acquired through engagement with the world, implying that to master a language, we should immerse ourselves in its use, not merely memorize its rules.

        The best immersion? Living abroad, if you have the means, though it's no guarantee. As adults, fear often inhibits playful learning, and unlike machines, pride can prevent us from learning from our errors. A practical approach is to consume extensive content in the target language. To stay engaged, choose content that interests you in your native language; if you don't enjoy classical literature in your mother tongue, there's no point starting with it in another.

        By engaging with foreign language content through text, audio, and video, you start to recognize more words, and the language begins to sound like, say, French, not just gibberish. Video adds context, linking sounds to visuals. Remember your frustration with that German movie? As language learners, we're more like toddlers learning their first language. You wouldn't show a two-year-old 'The Godfather' (nearly 3 hours long), but they could handle an episode of 'Sesame Street', with some zoning out. Aim for content that's meaningful to you, at a level that feels like play, just challenging enough to keep you coming back.

        What about grammar? Yes, it's necessary, but just like an English toddler quickly learns that 'We goed' isn't what mommy and daddy say, you'll pick up on grammar patterns naturally through extensive content consumption. Grammar resources should be reference tools, not the staple of your learning journey. Keep it playful and natural.
        </div>
        """, unsafe_allow_html=True)

    # Section: What is LanguageBuddy and why does it work?
    st.header(":orange[What is LanguageBuddy and why does it work?]")
    with st.expander("Why LanguageBuddy Works:"):
        st.markdown("""
        **LanguageBuddy** is an innovative language learning platform designed to make learning a new language both effective and enjoyable. Here's why it works:

        - **Real-World Context:** Instead of rote memorization, LanguageBuddy uses YouTube videos to provide meaningful context, helping you understand and retain new vocabulary and grammar.
        - **Personalized Experience:** You choose the content you want to watch, and LanguageBuddy keeps track of the vocabulary that matters to you by saving it in a cloud database. This allows you to download your personal vocabulary list or study flashcards tailored to your interests, adapting to your learning pace and focusing on areas where you need improvement for a truly personalized experience.
        - **Integrated Learning Tools:** With LanguageBuddy, once you've selected a YouTube video, you can access all the tools you need in one place: follow along with a transcript enhanced by tooltip translations, and review or download your personal vocabulary, making your learning journey smooth and efficient.
        """)

    # Section: How can I get more out of LanguageBuddy?
    st.header(":orange[How can I get more out of LanguageBuddy?]")
    with st.expander("To Maximize Your Learning with LanguageBuddy:"):
        st.markdown("""
        - **Daily Practice:** Language learning is like working a muscle; consistent daily use keeps your skills sharp and strong. Aim to review one video a day on LanguageBuddy.

        - **Curate Your Content:** Create a YouTube playlist to store interesting videos you want to review in LanguageBuddy. This saves time searching for new content each session, allowing you to focus on learning.

        - **Leverage All Features:** By choosing videos between 2 and 5 minutes, you'll access a transcript with translation tooltips, and your new vocabulary will be saved to the cloud. Review these words on the "Study Vocabulary" page. Also, track your learning journey by checking how many new words you've encountered and how your fluency has improved on the "Your Progress" page.

        - **Set Goals:** Define clear language learning goals. Think about how you want to use the language - whether for travel, work, or personal interest. Decide on the subjects you want to be able to talk about or understand, like discussing travel experiences, ordering food, or following the news, to guide your learning path and keep you motivated.

        - **Practice Speaking:** Improve your pronunciation and fluency by reading the video transcripts out loud. Try to imitate the sound bites from the videos to mimic native speakers. Additionally, find local speaking practice groups on [Meetup](https://www.meetup.com/) or [Facebook](https://www.facebook.com/) to practice with others in your area. For those with the means, hiring affordable one-on-one teachers on platforms like [Preply](https://preply.com/) or [italki](https://www.italki.com/) can provide personalized speaking practice.
        """)

    # Section: Why I made this app
    st.header(":orange[Why I made this app]")
    # with st.expander(":orange[Why I made LanguageBuddy]"):
    # Create two columns
    col1, col2 = st.columns([1, 2])
        
    with col1:
        st.image("photo.jpg", width=200, caption="Connor")
        
    st.markdown("""
    <style>
    @import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css");
    </style>
    """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        I created LanguageBuddy with a mission to share accessible language learning tools and methods with my friends, family, and the broader community of language learners. This project has been an exciting journey where I've channeled my love for learning French into something tangible, integrating it with the technical skills I'm gaining in my Master's of Computer Information Technology program at the University of Pennsylvania.
        """)
        st.markdown("""
        <a href="mailto:gentleconnor123@gmail.com"><i class="bi bi-envelope-fill" style="margin-right:5px;"></i>Contact Me</a>
        <br>
        <a href="https://www.linkedin.com/in/connor-gentle/"><i class="bi bi-linkedin" style="margin-right:5px;"></i>LinkedIn Profile</a>
        """, unsafe_allow_html=True)