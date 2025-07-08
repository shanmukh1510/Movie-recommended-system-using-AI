
import streamlit as st
import pandas as pd
import requests
import pickle

# Load the processed data and similarity matrix
try:
    with open('movie_data.pkl', 'rb') as file:
        movies, cosine_sim = pickle.load(file)
except FileNotFoundError:
    st.error("movie_data.pkl file not found!")
    raise
except Exception as e:
    st.error(f"Error loading pickle file: {e}")
    raise

# Function to get movie recommendations
def get_recommendations(title, cosine_sim=cosine_sim):
    try:
        idx = movies[movies['title'] == title].index[0]
    except IndexError:
        st.error("Movie title not found in the dataset.")
        return pd.DataFrame()  # Return empty dataframe in case of error
    
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]  # Get top 10 similar movies
    movie_indices = [i[0] for i in sim_scores]
    return movies[['title', 'movie_id']].iloc[movie_indices]

# Fetch movie poster from TMDB API with timeout handling
def fetch_poster(movie_id):
    api_key = '769c33c5c41dfdba7fb7ba2b04f059c3'  # Replace with your TMDB API key
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}'

    try:
        # Set a timeout of 5 seconds to avoid hanging indefinitely
        response = requests.get(url, timeout=5)  # Timeout added here
        response.raise_for_status()  # Raise exception for HTTP errors (4xx, 5xx)
        data = response.json()

        # Extract poster path and build full URL
        poster_path = data.get('poster_path', None)
        if poster_path:
            full_path = f"https://image.tmdb.org/t/p/w500{poster_path}"
            return full_path
        else:
            # Return placeholder image if no poster is found
            return 'https://via.placeholder.com/150'
    
    except requests.exceptions.Timeout:
        # Handle timeout exception by returning a fallback image URL
        return 'https://via.placeholder.com/150'
    except requests.exceptions.RequestException as e:
        # Handle any other request exception and return a fallback image URL
        return 'https://via.placeholder.com/150'

# Streamlit UI
st.title("Movie Recommendation System")

# Movie selection dropdown
selected_movie = st.selectbox("Select a movie:", movies['title'].values)

# Recommend button action
if st.button('Recommend'):
    if selected_movie in movies['title'].values:
        recommendations = get_recommendations(selected_movie)
        
        if not recommendations.empty:
            st.write("Top 10 recommended movies:")

            # Create a 2x5 grid layout for displaying posters and movie titles
            for i in range(0, 10, 5):  # Loop over rows (2 rows, 5 movies each)
                cols = st.columns(5)  # Create 5 columns for each row
                for col, j in zip(cols, range(i, i + 5)):
                    if j < len(recommendations):
                        movie_title = recommendations.iloc[j]['title']
                        movie_id = recommendations.iloc[j]['movie_id']
                        poster_url = fetch_poster(movie_id)
                        with col:
                            st.image(poster_url, width=130)
                            st.write(movie_title)
    else:
        st.error("Selected movie not found in the dataset.")
