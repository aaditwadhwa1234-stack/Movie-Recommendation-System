import streamlit as st
import pandas as pd
import requests
import pickle
import requests


with open('movie_data.pkl', 'rb') as file:
    movies, cosine_sim = pickle.load(file)


def get_recommendations(title, cosine_sim=cosine_sim):
    idx = movies[movies['title'] == title].index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]  
    movie_indices = [i[0] for i in sim_scores]
    return movies[['title', 'movie_id']].iloc[movie_indices]




def fetch_poster(movie_id):
    api_key = "b488b1d58c5e3fedbbebcc7debe1ce04"

    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return None

        data = response.json()

        poster_path = data.get("poster_path")

        if not poster_path:
            return None

        return f"https://image.tmdb.org/t/p/w500{poster_path}"

    except Exception as e:
        print(e)
        return None
    
def explain_recommendation(movie1, movie2):

    idx1 = movies[movies['title'] == movie1].index[0]
    idx2 = movies[movies['title'] == movie2].index[0]

    tags1 = set(movies.iloc[idx1]['tags'].split())
    tags2 = set(movies.iloc[idx2]['tags'].split())

    common_tags = list(tags1.intersection(tags2))

    similarity = cosine_sim[idx1][idx2]

    reasons = [
        f"Similarity Score: {similarity*100:.1f}%"
    ]

    if common_tags:
        reasons.append(
            f"Shared features: {', '.join(common_tags[:5])}"
        )

    return reasons

st.title("Movie Recommendation System")

selected_movie = st.selectbox("Select a movie:", movies['title'].values)

if st.button('Recommend'):
    recommendations = get_recommendations(selected_movie)
    st.write("Top 10 recommended movies:")

    
    for i in range(0, 10, 5):  
        cols = st.columns(5)  
        for col, j in zip(cols, range(i, i+5)):
            if j < len(recommendations):
                movie_title = recommendations.iloc[j]['title']
                movie_id = recommendations.iloc[j]['movie_id']
                poster_url = fetch_poster(movie_id)
                with col:
                    if poster_url:
                        st.image(poster_url, width=130)
                    else:
                        st.write("Poster not available")
                    st.write(movie_title)
                    with st.expander("Why recommended?"):
                        reasons = explain_recommendation(
                            selected_movie,
                            movie_title
                        )

                        for reason in reasons:
                            st.write("✓", reason)
