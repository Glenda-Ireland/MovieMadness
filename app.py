

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("Movie Madness Dashboard")

#adding sidebar navigation
app_mode = st.sidebar.radio("Choose App", ["Movie Recommender", "Genre Time Series", "Book-Based Movies"])



#App for Movie Recommender 
if app_mode == "Movie Recommender":
    st.subheader("Movie Recommender")

    #loading the dataset 
    movies = pd.read_pickle("https://raw.github.com/Glenda-Ireland/MovieMadness/main/movies.pkl")
    similarity_with_item = pd.read_pickle("https://raw.github.com/Glenda-Ireland/MovieMadness/main/similarity_with_item.pkl")

    valid_movie_ids = similarity_with_item.columns 
    movies_filtered = movies[movies["movieId"].isin(valid_movie_ids)]


    #dictionary
    title_to_id = movies_filtered.set_index("title")["movieId"].to_dict()
    id_to_title = movies_filtered.set_index("movieId")["title"].to_dict()

    #function for the logic of recommending 
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

    if recommendations is not None and not recommendations.empty:
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

# App 2 Genre Time series
elif app_mode == "Genre Time Series":
    st.subheader("Average Ratings per Genre Over Time")
    @st.cache_data
    def load_data():
        return pd.read_pickle("https://raw.github.com/Glenda-Ireland/MovieMadness/main/movie_vis.pkl")
    df = load_data()
    df["genres"] = df["genres"].str.split("|")
    df = df.explode("genres")
    selected_genre = st.selectbox("Choose a Genre", sorted(df["genres"].dropna().unique()))
    genre_df = df[df["genres"] == selected_genre]
    avg_ratings = genre_df.groupby("Month_Year")["rating"].mean().reset_index()
    fig, ax = plt.subplots()
    ax.plot(avg_ratings["Month_Year"], avg_ratings["rating"], marker="o")
    ax.set_title(f"Average Rating Over Time: {selected_genre}")
    ax.set_xlabel("Month and Year")
    ax.set_ylabel("Average Rating")
    plt.xticks(rotation=45)
    st.pyplot(fig)
    


#App 3: Book Based
elif app_mode == "Book-Based Movies":
    st.subheader("Movies Based on Books")
    @st.cache_data
    def load_data1():
        return pd.read_pickle("https://raw.github.com/Glenda-Ireland/MovieMadness/main/clean_book.pkl")
    df1 = load_data1()
    df1["genres"] = df1["genres"].str.split("|")
    df1 = df1.explode("genres")
    genre_options = sorted(df1["genres"].dropna().unique())
    selected_genre1 = st.selectbox("Choose a Genre", genre_options)
    results1 = df1[df1["genres"] == selected_genre1]["title", "tag"].drop_duplicates()
    st.write(f"Movies Based on Books in Genre: {selected_genre1}")
    if not results1.empty:
        st.dataframe(results1)
    else:
        st.write("No results found for this Genre")