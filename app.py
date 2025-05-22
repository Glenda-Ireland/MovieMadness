import streamlit as st
import pandas as pd

st.title("Movie Madness")

#loading the dataset 
movies = pd.read_csv("https://raw.github.com/Glenda-Ireland/MovieMadness/main/movie_vis.csv")
similarity_with_item = pd.read_csv("https://raw.github.com/Glenda-Ireland/MovieMadness/main/similarity_with_item.csv")
valid_movie_ids = similarity_with_item.columns
movies["movieId"] = movies["movieId"]
movies_filtered = movies[movies["movieId"].isin(valid_movie_ids)]




title_to_id = movies_filtered.set_index("title")["movieId"].to_dict()
id_to_title = movies_filtered.set_index("movieId")["title"].to_dict()
def get_similar_movies(movie_title, n=10):
    movie_id = title_to_id.get(movie_title)
    if movie_id not in similarity_with_item:
        return pd.DataFrame()
    similar_scores = similarity_with_item[movie_id].dropna().sort_values(ascending=False).head(n)
    similar_ids = similar_scores.index
    result = movies[movies["movieId"].isin(similar_ids)].copy()
    result["Similarity"] = result["movieId"].map(similar_scores)
    result = result.sort_values(by="Similarity", ascending=False)
    return result.reset_index(drop=True)

st.title("Select A Movie You Enjoy- Find a Recommendation")

movie_list = sorted(title_to_id.keys())
selected_movie = st.selectbox("Pick a movie", movie_list)
num_recs = st.slider("Number of Similar Movies", 5, 20, 10)

if selected_movie:
    st.subheader(f"Similar Movies to: {selected_movie}")
    recommendations = get_similar_movies(selected_movie, num_recs)
    if not recommendations.empty:
        st.dataframe(recommendations[["title", "genres", "Similarity"]])
        genres_all = sorted(set(
            g for sublist in recommendations["genres"].dropna().str.split("|") for g in sublist
        ))
        selected_genres = st.multiselect("Filter by Genre", genres_all)

        if selected_genres:
            recommendations =recommendations[recommendations["genres"].str.contains("|".join(selected_genres))]

        st.subheader(f"Similar Movies to: {selected_movie}")

        for _, row in recommendations.iterrows():
            similarity = f"{row["Similarity"]:.3f}"
            genres = row["genres"].replace("|", ", ")
            st.markdown(f"""
                <div style="border:1px solid #ddd; border-radius:10px; padding:15px; margin-bottom:15px; background-color:#f9f9f9">
                    <h4 style="color:#2c3e50;">{row["title"]}</h4>
                    <p><strong>Genres:</strong> <span style="color:#ec7e22;">{genres}</span></p>
                    <p><strong>Similarity Score:</strong> <span style="color:#27ae60:">{similarity}</span></p>
               </div>
            """, unsafe_allow_html=True)

    else:
        st.write("No similar movies found")

