

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.cm as cm
from matplotlib.collections import LineCollection
import numpy as np

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
    genre_df["Month_Year"] = pd.to_datetime(genre_df["Month_Year"], format="%m/%Y")
    genre_df["Year"] = genre_df["Month_Year"].dt.year
    avg_ratings = genre_df.groupby("Year")["rating"].mean().reset_index()
    fig, ax = plt.subplots()
    count_ratings = genre_df.groupby("Year")["rating"].count().reset_index(name="count")
    avg_ratings = avg_ratings.merge(count_ratings, on="Year")
    #adding colors to make it more targeted for audience and better to see how many ratings, this means I had to count the ratings and create seperation
    cmap = cm.get_cmap("magma")
    norm = mcolors.Normalize(vmin=avg_ratings["count"].min(), vmax=avg_ratings["count"].max())
    points = np.array([avg_ratings["Year"], avg_ratings["rating"]]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    colors = cmap(norm(avg_ratings["count"].iloc[:-1]))
    lc = LineCollection(segments, colors=colors, linewidths=2)
    ax.add_collection(lc)
    sc = ax.scatter(avg_ratings["Year"], avg_ratings, c=avg_ratings["count"], cmap="magma", edgecolor="black")
    ax.set_xlim(avg_ratings["Year"].min(), avg_ratings["Year"].max())
    ax.set_ylim(avg_ratings["rating"].min() - 0.1, avg_ratings["rating"].max() + 0.1)
    plt.colorbar(sc, ax=ax, label="Number of Ratings")
    ax.set_title(f"Average Rating Over Time: {selected_genre}")
    ax.set_xlabel("Year")
    ax.set_ylabel("Average Rating")
    plt.xticks(rotation=45)
    st.pyplot(fig)
    


#App 3: Book Based
elif app_mode == "Book-Based Movies":
    st.subheader("Movies Based on Books")
    @st.cache_data
    def load_data1():
        return pd.read_pickle("https://raw.github.com/Glenda-Ireland/MovieMadness/main/bookish.pkl")
    df1 = load_data1()
    df1["genres"] = df1["genres"].str.split("|")
    df1 = df1.explode("genres")
    genre_options = sorted(df1["genres"].dropna().unique())
    selected_genre1 = st.selectbox("Choose a Genre", genre_options)
    results1 = df1[df1["genres"] == selected_genre1][["title", "tag"]].drop_duplicates()
    st.write(f"Movies Based on Books in Genre: {selected_genre1}")
    if not results1.empty:
        st.dataframe(results1)
    else:
        st.write("No results found for this Genre")

#this took an insane amount of time, i have nothing but respect for those who make dashboards
#matplotlib and streamlit tutorials definitely helped but it was still very painful
#every single little tiny error had to be fixed.  