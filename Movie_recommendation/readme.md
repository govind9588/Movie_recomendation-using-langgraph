🎬 Movie Recommendation Agent (Streamlit + Gemini + LangGraph)

This project is an interactive Movie Recommendation Web App built using:

✅ Streamlit for UI
✅ LangGraph for agent logic
✅ Gemini 2.5 Flash (Google Generative AI) for smart movie summaries
✅ Wikipedia Movie Dataset for movie selection

It allows users to search for movies by year, genre, and count, and displays AI-generated recommendations in a beautiful UI.

🚀 Features

🎯 Search movies by year, genre, and number of results

🤖 AI-generated descriptions, ratings & comparisons using Gemini

🧠 LangGraph-powered conversational structure

🎨 Stunning UI with custom CSS

📜 Session history tracking

🔄 Reset and clear history options

🧾 Markdown-based Gemini output

🛠 Exception and error handling

🗂️ Project Structure
movie_recommendation_app/
│
├── ui.py # Main Streamlit + LangGraph application
├── README.md # This file

🔧 Installation & Setup
✅ 1. Clone or Download the Project

✅ 2. Install Required Packages
pip install streamlit langgraph langchain-core langchain-google-genai requests

✅ 3. Add Your Google Gemini API Key

Replace the API key in:

google_api_key="YOUR_API_KEY_HERE"

Or set it as an environment variable:

export GOOGLE_API_KEY=your_api_key

✅ 4. Run the App
streamlit run app.py

🖼️ How It Works
✅ 1. Sidebar Inputs

Year (e.g., 2010, 2015, 2005)

Genre (optional)

Number of movies

Click 🎬 Get Recommendations!

✅ 2. What Happens Behind the Scenes

Filter movies from the Wikipedia Movie Dataset (JSON)

Randomly select movies

Ask Gemini to return:

Short descriptions

Rating out of 10

Genre-based tone

Best pick + link

Output as a Markdown table

✅ 3. See AI Results

Gemini recommendations

Movie cards (UI-friendly)

History tracking in the sidebar

📸 UI Preview (Highlights)

Custom CSS (gradient backgrounds, cards, buttons)

Recommendation box with Gemini output

Movie cards displayed in 2 columns

Sidebar with parameters & history

✅ Example Gemini Output Table
| Title | Genre | Year | Recommendation | Rating/10 |
|-------------|--------|------|-----------------------------|-----------|
| Inception | Action | 2010 | A thrilling mind-bender... | 9/10 |

❗ Error Handling

If no movies match:

No movies found for that year/genre. Try a different year or remove the genre filter.

🧹 Reset & History

✅ Reset clears session state

✅ Clear History wipes previous results

🏁 Future Improvements (Optional)

Add trailers or posters via API

Add filters (language, director)

Export recommendations to PDF

💡 Credits

Movie Data: Wikipedia (public dataset)

AI Model: Gemini 2.5 Flash

Frameworks: Streamlit, LangGraph, LangChain

Author: Yogesh (as shown in UI)
