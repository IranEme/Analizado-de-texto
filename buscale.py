import altair as alt
import pandas as pd
import streamlit as st
import sqlite3
import re
from thefuzz import fuzz
from collections import defaultdict
st.set_page_config(page_title="Smart Art Analyzer", layout="centered", page_icon="🎨")
DB_NAME = "artes.db"
ARTWORKS_TABLE_NAME = "artes"
KEYWORDS_TABLE_NAME = "subtopic_keywords"
FUZZY_SCORE_THRESHOLD = 75
@st.cache_data
def load_inference_map_from_db():
    conn = sqlite3.connect(f"file:{DB_NAME}?mode=ro", uri=True)
    try:
        df = pd.read_sql_query(f"SELECT keyword, subtopic FROM {KEYWORDS_TABLE_NAME}", conn)
        inference_map = defaultdict(list)
        for index, row in df.iterrows():
            inference_map[row['subtopic']].append(row['keyword'])
        return dict(inference_map)
    finally:
        conn.close()
def infer_subtopic(query: str, inference_map: dict) -> str | None:
    if not query or not isinstance(query, str):
        return None
    query_lower = query.lower()
    for subtopic, keywords in inference_map.items():
        if any(re.search(r'\b' + keyword + r'\b', query_lower) for keyword in keywords):
            return subtopic
    return None
def search_dataframe(search_str: str, subtopic: str | None = None) -> pd.DataFrame:
    conn = sqlite3.connect(DB_NAME)
    search_pattern = f"%{search_str}%"
    base_query = f"SELECT * FROM {ARTWORKS_TABLE_NAME} WHERE (title_e LIKE ? OR journal LIKE ?)"
    if subtopic:
        query = f"{base_query} AND subtopic = ?"
        params = (search_pattern, search_pattern, subtopic)
    else:
        query = base_query
        params = (search_pattern, search_pattern)
    results_df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return results_df
def rank_by_fuzziness(df: pd.DataFrame, query: str) -> pd.DataFrame:
    if df.empty:
        return df
    scores = df.apply(
        lambda row: max(
            fuzz.partial_ratio(query.lower(), str(row['title_e']).lower()),
            fuzz.partial_ratio(query.lower(), str(row['journal']).lower())
        ),
        axis=1
    )
    df['score'] = scores
    ranked_df = df[df['score'] >= FUZZY_SCORE_THRESHOLD].sort_values(by='score', ascending=False)
    return ranked_df
def generate_barplot(results: pd.DataFrame, count_column: str, top_n: int = 10):
    if results.empty:
        return None
    return alt.Chart(results).transform_aggregate(
        count='count()',
        groupby=[f'{count_column}']
    ).transform_window(
        rank='rank(count)',
        sort=[alt.SortField('count', order='descending')]
    ).transform_filter(
        alt.datum.rank < top_n
    ).mark_bar().encode(
        y=alt.Y(f'{count_column}:N', sort='-x', title="Subtopic"),
        x=alt.X('count:Q', title="Number of Artworks"),
        tooltip=[f'{count_column}:N', 'count:Q']
    ).properties(
        title=f"Top {top_n} Subtopics in Search Results",
        width=700,
        height=400
    ).interactive()
def app():
    st.title("Smart Art Analyzer 🎨")
    st.write("Search for an artwork. The app tolerates typos and tries to find the most relevant results.")
    try:
        inference_map = load_inference_map_from_db()
    except Exception as e:
        st.error(f"Failed to load keyword dictionary from database '{DB_NAME}'.")
        st.info(f"Please run 'python3 create_artes_db.py' first to create and populate the database.")
        return
    with st.form(key='Search'):
        text_query = st.text_input(label='Enter search term (e.g., "Monet portrat" or "bronze statue")')
        submit_button = st.form_submit_button(label='Search')
    if submit_button and text_query:
        with st.spinner("Searching and ranking results..."):
            inferred_topic = infer_subtopic(text_query, inference_map)
            candidate_results = search_dataframe(text_query, subtopic=inferred_topic)
            final_results = rank_by_fuzziness(candidate_results, text_query)
            if inferred_topic:
                st.info(f"Detected keyword for **{inferred_topic}**. Searching within this subtopic.")
            else:
                st.info("No specific subtopic detected. Searching across all categories.")
            st.success(f"Found **{len(final_results):,}** relevant results, ranked by similarity.")
        if not final_results.empty:
            st.write("### Search Results (ranked by relevance)")
            display_df = final_results[['title_e', 'journal', 'subtopic', 'score']].rename(
                columns={'title_e': 'Title', 'journal': 'Medium', 'subtopic': 'Subtopic', 'score': 'Relevance Score'}
            )
            st.dataframe(display_df.head(20))
            st.write("### Subtopic Distribution in Results")
            chart = generate_barplot(final_results, "subtopic", 10)
            if chart:
                st.altair_chart(chart)
        else:
            st.warning("No relevant results found. Try a different search term.")
if __name__ == '__main__':
    app()