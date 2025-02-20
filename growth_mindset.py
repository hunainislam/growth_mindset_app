import streamlit as st
import datetime
import random
import json
import uuid
from collections import defaultdict
from streamlit_option_menu import option_menu
from typing import Dict, List, Optional

# Constants
DATA_FILE = "app_data.json"
GROWTH_QUOTES = [
    "The only limit to our realization of tomorrow will be our doubts of today. - Franklin D. Roosevelt",
    "Becoming is better than being. - Carol Dweck",
    "It's not that I'm so smart, it's that I stay with problems longer. - Albert Einstein"
]
DAILY_CHALLENGES = {
    "Beginner": [
        "Reflect on one mistake and what it taught you",
        "Try a new learning method for 30 minutes"
    ],
    "Advanced": [
        "Teach a concept to someone else",
        "Tackle a problem outside your comfort zone"
    ]
}

# Data Models
class JournalEntry:
    def __init__(self, date: str, reflection: str, lessons: str, mood: str, tags: List[str]):
        self.id = str(uuid.uuid4())
        self.date = date
        self.reflection = reflection
        self.lessons = lessons
        self.mood = mood
        self.tags = tags

class CommunityPost:
    def __init__(self, content: str, author: str):
        self.id = str(uuid.uuid4())
        self.date = datetime.datetime.now().isoformat()
        self.content = content
        self.author = author
        self.likes = 0

# Data Persistence
def load_data() -> Dict:
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "journal_entries": [],
            "completed_challenges": [],
            "community_posts": [],
            "users": {}
        }

def save_data(data: Dict) -> None:
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# Utility Functions
def calculate_streak(dates: List[str]) -> int:
    if not dates:
        return 0
    
    sorted_dates = sorted([datetime.date.fromisoformat(d) for d in dates])
    streak = 1
    current_date = datetime.date.today()
    
    for date in reversed(sorted_dates):
        if date == current_date:
            continue
        if current_date - date == datetime.timedelta(days=1):
            streak += 1
            current_date = date
        else:
            break
    return streak

def get_weekly_progress() -> Dict[str, int]:
    data = load_data()
    challenges = data["completed_challenges"]
    
    progress = defaultdict(int)
    today = datetime.date.today()
    
    for i in range(7):
        date = today - datetime.timedelta(days=i)
        progress[date.isoformat()] = 0
    
    for challenge in challenges:
        date = challenge["date"]
        progress[date] += 1
    
    return progress

# Authentication
def authenticate_user() -> Optional[str]:
    data = load_data()
    with st.sidebar:
        if 'authenticated' not in st.session_state:
            st.subheader("User Login")
            username = st.text_input("Username")
            if st.button("Login/Create Account"):
                if username:
                    st.session_state.authenticated = username
                    if username not in data["users"]:
                        data["users"][username] = {"joined": datetime.date.today().isoformat()}
                        save_data(data)
                    st.rerun()
            return None
        else:
            st.subheader(f"Welcome, {st.session_state.authenticated}")
            if st.button("Logout"):
                del st.session_state.authenticated
                st.rerun()
            return st.session_state.authenticated

# App Components
def dashboard() -> None:
    st.header("🧠 Growth Mindset Dashboard")
    st.subheader("Daily Inspiration")
    st.success(random.choice(GROWTH_QUOTES))
    
    with st.expander("📚 Growth Mindset Fundamentals"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **Core Principles:**
            - Intelligence can be developed
            - Challenges are opportunities
            - Effort leads to mastery
            - Feedback is constructive
            - Others' success inspires
            """)
        with col2:
            st.video("https://www.youtube.com/watch?v=hiiEeMN7vbQ")
    
    with st.expander("📈 Quick Actions"):
        action_cols = st.columns(3)
        with action_cols[0]:
            if st.button("🎯 New Challenge"):
                challenge_level = random.choice(list(DAILY_CHALLENGES.keys()))
                st.session_state.current_challenge = random.choice(
                    DAILY_CHALLENGES[challenge_level]
                )
        with action_cols[1]:
            if st.button("📝 Quick Journal"):
                st.session_state.journal_quick_entry = True

def daily_challenge(username: str) -> None:
    st.header("🔥 Daily Growth Challenge")
    challenge_level = st.selectbox("Select Difficulty", list(DAILY_CHALLENGES.keys()))
    
    if st.button("Generate New Challenge"):
        challenge = random.choice(DAILY_CHALLENGES[challenge_level])
        st.session_state.current_challenge = challenge
    
    if 'current_challenge' in st.session_state:
        with st.container(border=True):
            st.subheader("Today's Challenge")
            st.markdown(f"#### {st.session_state.current_challenge}")
            
            if st.button("Complete Challenge ✅"):
                data = load_data()
                data["completed_challenges"].append({
                    "date": datetime.date.today().isoformat(),
                    "challenge": st.session_state.current_challenge,
                    "user": username
                })
                save_data(data)
                st.success("Challenge completed! 🎉")
                del st.session_state.current_challenge
                st.rerun()

def progress_tracker(username: str) -> None:
    st.header("📈 Progress Tracker")
    data = load_data()
    user_challenges = [c for c in data["completed_challenges"] if c["user"] == username]
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Challenges", len(user_challenges))
    col2.metric("Current Streak", calculate_streak([c["date"] for c in user_challenges]))
    
    # Progress Visualization
    with st.expander("📊 Detailed Analytics"):
        progress = get_weekly_progress()
        st.bar_chart(progress)

def reflection_journal(username: str) -> None:
    st.header("📔 Reflection Journal")
    data = load_data()
    
    with st.form("journal_entry"):
        entry_date = st.date_input("Entry Date", datetime.date.today())
        reflection = st.text_area("Today's Reflection", height=200)
        lessons = st.text_input("Key Lessons Learned")
        mood = st.select_slider("Daily Mood", ["😞", "😐", "😊", "😁"])
        tags = st.multiselect("Tags", ["Learning", "Challenge", "Breakthrough", "Struggle"])
        
        if st.form_submit_button("Save Entry"):
            new_entry = {
                "id": str(uuid.uuid4()),
                "date": entry_date.isoformat(),
                "reflection": reflection,
                "lessons": lessons,
                "mood": mood,
                "tags": tags,
                "user": username
            }
            data["journal_entries"].append(new_entry)
            save_data(data)
            st.success("Entry saved successfully!")
    
    with st.expander("📖 View Past Entries"):
        search_query = st.text_input("Search Entries")
        filtered_entries = [
            e for e in data["journal_entries"]
            if e["user"] == username and (
                search_query.lower() in e["reflection"].lower() or
                search_query.lower() in e["lessons"].lower()
            )
        ]
        
        for entry in reversed(filtered_entries):
            st.markdown(f"**{entry['date']}** {entry['mood']}")
            st.write(entry["reflection"])
            st.caption(f"Lessons: {entry['lessons']}")
            st.caption(f"Tags: {', '.join(entry['tags'])}")
            if st.button(f"Delete {entry['id'][:8]}", key=f"del_{entry['id']}"):
                data["journal_entries"] = [e for e in data["journal_entries"] if e["id"] != entry["id"]]
                save_data(data)
                st.rerun()
            st.divider()

def community_wall(username: str) -> None:
    st.header("🌍 Community Wisdom Wall")
    data = load_data()
    
    with st.form("community_post"):
        post = st.text_area("Share your growth mindset experience")
        if st.form_submit_button("Post to Community"):
            new_post = {
                "id": str(uuid.uuid4()),
                "date": datetime.datetime.now().isoformat(),
                "content": post,
                "author": username,
                "likes": 0
            }
            data["community_posts"].append(new_post)
            save_data(data)
    
    st.subheader("Recent Community Posts")
    search_query = st.text_input("Search Posts")
    
    for post in reversed(data["community_posts"]):
        if search_query.lower() in post["content"].lower():
            col1, col2 = st.columns([0.9, 0.1])
            with col1:
                st.markdown(f"**{post['author']}** ({post['date']})")
                st.write(post["content"])
            with col2:
                st.markdown(f"❤️ {post['likes']}")
                if st.button("👍", key=f"like_{post['id']}"):
                    post["likes"] += 1
                    save_data(data)
                    st.rerun()
            if post["author"] == username and st.button(f"Delete {post['id'][:8]}", key=f"del_{post['id']}"):
                data["community_posts"] = [p for p in data["community_posts"] if p["id"] != post["id"]]
                save_data(data)
                st.rerun()
            st.divider()

def resources() -> None:
    st.header("📚 Growth Resources")
    
    with st.expander("Recommended Reading"):
        st.markdown("""
        - Mindset: The New Psychology of Success - Carol Dweck
        - Grit: The Power of Passion and Perseverance - Angela Duckworth
        """)
    
    with st.expander("Learning Videos"):
        st.video("https://www.youtube.com/watch?v=M1CHPnZfFmU")
    
    with st.expander("Interactive Tools"):
        if st.button("Take Growth Mindset Assessment"):
            st.switch_page("pages/assessment.py")

# Main App
def main():
    st.set_page_config(
        page_title="Growth Mindset Lab",
        page_icon="🧠",
        layout="wide"
    )
    
    username = authenticate_user()
    if not username:
        return
    
    with st.sidebar:
        choice = option_menu(
            "Growth Mindset Lab",
            ["Dashboard", "Daily Challenge", "Progress Tracker", 
             "Reflection Journal", "Community Wall", "Resources"],
            icons=['house', 'clock', 'graph-up', 'journal', 'people', 'book'],
            menu_icon="brain",
            default_index=0,
            styles={
                "container": {"padding": "5px"},
                "nav-link": {"font-size": "16px"}
            }
        )
    
    if choice == "Dashboard":
        dashboard()
    elif choice == "Daily Challenge":
        daily_challenge(username)
    elif choice == "Progress Tracker":
        progress_tracker(username)
    elif choice == "Reflection Journal":
        reflection_journal(username)
    elif choice == "Community Wall":
        community_wall(username)
    elif choice == "Resources":
        resources()

if __name__ == "__main__":
    main()