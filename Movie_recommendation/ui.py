import streamlit as st
from langgraph.graph import StateGraph, END
from langchain_core.tools import Tool
from typing import TypedDict, Optional, Literal, List
import requests
import random
import re
from langchain_google_genai import ChatGoogleGenerativeAI  

class MovieState(TypedDict):
    year: Optional[str]
    movie: Optional[str]
    next_action: Optional[Literal["continue", "exit"]]
    history: List[str]
    count: int
    genre: Optional[str]

# ----------------------
# Movie tool function
# ----------------------
def movie_tool(year: str, count: int = 5, genre: str = None) -> dict:
    url = "https://raw.githubusercontent.com/prust/wikipedia-movie-data/master/movies.json"
    movies = requests.get(url).json()

    # Filter by year
    year_int = int(year)
    filtered = [m for m in movies if m["year"] == year_int]
    print(f"[DEBUG] movie_tool called -> year={year}, count={count}, genre={genre}")

    # Filter by genre if provided
    if genre:
        filtered = [m for m in filtered if genre.lower() in [g.lower() for g in m.get("genres", [])]]

    # Random selection
    chosen_movies = random.sample(filtered, min(count, len(filtered)))
    movie_list = [f"{m['title']} ({m['year']})" for m in chosen_movies]
 
    if not chosen_movies:
        return {
            "movies": [],
            "llm_recommendations": "No movies found for that year/genre. Try a different year or remove the genre filter."
        }

    # Gemini LLM recommendation
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.7,
        google_api_key="AIzaSyDGcDBJjKJKfWRlkAzM_Gfk54MbC0fW3QM"
    )

    prompt = f"""
    Here are some movies: {', '.join([m['title'] for m in chosen_movies])}.
    For each movie:
    - Give a short (max 2 sentences) recommendation or description.
    - Style depends on genre: comedy = funny, horror = spooky, drama = emotional, action = thrilling, romance = heartfelt.
    - Add a rating out of 10.
    - Mention release year if available.

    Then:
    - Identify the best and top-rated movie among them.
    - Provide a one-line comparison of why it stands out.
    - Include a link to the rating source for the best movie.

    Return the results as a Markdown table with columns:
    Title | Genre | Year | Recommendation | Rating/10 |
    """


    llm_recommendations = llm.invoke(prompt).content
    return {"movies": movie_list, "llm_recommendations": llm_recommendations}

movie_tool_agent = Tool(
    name="MovieTool",
    description="Returns random movies from a given year and genre + Gemini recommendations",
    func=movie_tool
)

def ask_user_query(state: MovieState) -> MovieState:
    query = input("Enter your movie request (e.g., '5 action movies from 2015'): ").strip()

    year_match = re.search(r"\b(19|20)\d{2}\b", query)
    count_match = re.search(r"\b\d+\b", query)
    genre_match = re.search(r"(action|comedy|drama|horror|romance|thriller|animation)", query, re.I)

    state["year"] = year_match.group(0) if year_match else None
    state["count"] = int(count_match.group(0)) if count_match else 5
    state["genre"] = genre_match.group(0).lower() if genre_match else None

    return state

def suggest_movie(state: MovieState) -> MovieState:
    result = movie_tool_agent.func(
        year=state["year"],
        count=state["count"],
        genre=state["genre"]
    )

    state["movie"] = ", ".join(result["movies"])
    state["history"].extend(result["movies"])

    print("\nSuggested movies:", state["movie"])
    print("\nGemini Recommendations:\n", result["llm_recommendations"])
    return state

def should_continue(state: MovieState) -> MovieState:
    state["next_action"] = input("\nType 'continue' for another recommendation or 'exit' to stop: ").strip().lower()
    return state

def decide_route(state: MovieState) -> str:
    # Return the exact node name used in graph.add_node(...)
    return "ask_user_query" if state["next_action"] == "continue" else END

graph = StateGraph(MovieState)
graph.add_node("ask_user_query", ask_user_query)
graph.add_node("suggest_movie", suggest_movie)
graph.add_node("should_continue", should_continue)

graph.set_entry_point("ask_user_query")
graph.add_edge("ask_user_query", "suggest_movie")
graph.add_edge("suggest_movie", "should_continue")
graph.add_conditional_edges("should_continue", decide_route)

# Run the agent (COMMENTED OUT FOR STREAMLIT)
# ----------------------
# Uncomment these lines to run the original CLI version:
# state = {"year": None, "movie": None, "next_action": None, "history": [], "count": 5, "genre": None}
# app = graph.compile()
# app.invoke(state)
# if state["history"]:
#     print("\nMovie history from this session:")
#     for idx, movie in enumerate(state["history"], 1):
#         print(f"{idx}. {movie}")

# =====================================================
# STREAMLIT UI - NEW ADDITION
# =====================================================

st.set_page_config(
    page_title="Movie Recommendation Agent",
    page_icon="🎬",
    layout="wide"
)

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = []

# Custom CSS
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stButton>button {
        background-color: #fbbf24;
        color: #1f2937;
        font-weight: bold;
        border-radius: 10px;
        padding: 10px 24px;
    }
    .stButton>button:hover {
        background-color: #f59e0b;
        transform: scale(1.05);
    }
    .movie-card {
        background-color: rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .recommendation-box {
        background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
        padding: 20px;
        border-radius: 15px;
        margin: 20px 0;
        color: #1f2937;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

# Header
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("# 🎬 Yogesh Movie Recommendation Agent")
    st.markdown("### Powered by LangGraph & Gemini AI")

st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("🔍 Search Parameters")
    
    year = st.number_input(
        "📅 Year",
        min_value=1900,
        max_value=2100,
        value=2015,
        step=1,
        help="Enter the year of movies"
    )
    
    count = st.slider(
        "🎯 Number of Movies",
        min_value=1,
        max_value=10,
        value=5,
        help="How many movies do you want?"
    )
    
    genre = st.selectbox(
        "🎭 Genre (Optional)",
        ["", "Action", "Comedy", "Drama", "Horror", "Romance", "Thriller", "Animation"],
        help="Filter by genre"
    )
    
    st.markdown("---")
    
    search_button = st.button("🎬 Get Recommendations", use_container_width=True)
    reset_button = st.button("🔄 Reset", use_container_width=True)
    
    st.markdown("---")
    
    # History
    st.header("📜 Session History")
    if st.session_state.history:
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.history = []
            st.rerun()
        
        st.markdown(f"**Total movies: {len(st.session_state.history)}**")
        with st.expander("View All Movies"):
            for idx, movie in enumerate(st.session_state.history, 1):
                st.markdown(f"{idx}. {movie}")
    else:
        st.info("No history yet. Start searching!")

# Main content
if reset_button:
    st.session_state.history = []
    st.rerun()

if search_button:
    if not year:
        st.error(" Please enter a valid year!")
    else:
        with st.spinner("🔍 Yogesh Bot Searching for amazing movies..."):
            try:
                # Use your original movie_tool_agent function
                genre_lower = genre.lower() if genre else None
                result = movie_tool_agent.func(
                    year=str(year),
                    count=count,
                    genre=genre_lower
                )
                
                if not result['movies']:
                    st.warning(result['llm_recommendations'])
                else:
                    # Add to history
                    st.session_state.history.extend(result['movies'])
                    
                    # Display AI Recommendations
                    st.markdown("##  Bhatt shaab Recommendations")
                    st.markdown(f"""
                        <div class="recommendation-box">
                            ✨ {result['llm_recommendations']}
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Display movies
                    st.markdown("##  Recommended Movies")
                    
                    # Create columns for movie cards
                    cols = st.columns(2)
                    for idx, movie in enumerate(result['movies']):
                        with cols[idx % 2]:
                            st.markdown(f"""
                                <div class="movie-card">
                                    <h3> {movie}</h3>
                                </div>
                            """, unsafe_allow_html=True)
                    
                    st.success(f" Found {len(result['movies'])} movies from {year}!")
                    
            except Exception as e:
                st.error(f" Error: {str(e)}")
                st.info(" Tip: Try a different year or remove the genre filter")
else:
    # Welcome message
    st.markdown("""
        <div style='text-align: center; padding: 50px; background-color: rgba(255, 255, 255, 0.1); border-radius: 15px; margin: 20px 0;'>
            <h2 style='color: white;'> Welcome to Movie Recommendation Agent!</h2>
            <p style='color: #e5e7eb; font-size: 18px;'>
                Select a year, choose the number of movies, optionally pick a genre,<br>
                and click "Get Recommendations" to discover amazing films!
            </p>
            <p style='color: #fbbf24; font-size: 16px; margin-top: 20px;'>
                ⬅ Use the sidebar to get started
            </p>
        </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #e5e7eb; padding: 20px;'>
        <p>Built with LangGraph, Gemini AI & Streamlit | Movie Data from Wikipedia</p>
    </div>
""", unsafe_allow_html=True)