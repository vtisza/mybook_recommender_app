from re import escape
import streamlit as st
import pandas as pd
import numpy as np
import itertools

def make_link(text):
    return f"<a target='_blank' href={text}>{text}</a>"

@st.cache_data
def load_data():
    my_recommendations = pd.read_parquet('./data/my_recommendations.p')

    flattened_list = itertools.chain.from_iterable(my_recommendations['book_tags'])
    book_tags = list(set(flattened_list))
    
    book_tags = list(book_tags)
    book_tags = [book_tag.strip() for book_tag in book_tags]
    book_tags = list(set(book_tags))
    book_tags.sort()

    my_recommendations["rating_count"] = my_recommendations["rating_count"].rank(method='min', pct=True)*100
    min_read, max_read = int(my_recommendations['rating_count'].min()), int(my_recommendations['rating_count'].max())

    my_recommendations['url'] = my_recommendations['url'].apply(lambda x: make_link(x))

    return my_recommendations, book_tags, min_read, max_read

my_recommendations, book_tags, min_read, max_read = load_data()

st.title('Viktor konyvajanlo')
selected_tags = st.multiselect("Kivalasztott cimke", book_tags,)
filtered_tags = st.multiselect("Filterezett cimke", book_tags)
is_recommended = st.radio('Tipus', ["Ajanlott", "Nem ajanlott"])
selected_user = st.selectbox("User", ['Orsi', 'Viktor'])
min_read_s, max_read_s = st.slider('Olvasottsag (percentils)', min_read, max_read, value= [min_read, max_read])

if st.button('Ajanlj konyvet'):
    if selected_tags:
        selected_idx = my_recommendations["book_tags"].apply(lambda x: set(selected_tags).issubset(set(x)))
    else:
        selected_idx = np.repeat(True, my_recommendations.shape[0])

    if filtered_tags:
        filtered_idx = my_recommendations["book_tags"].apply(lambda x: bool(set(x) & set(filtered_tags)))
    else:
        filtered_idx = np.repeat(False, my_recommendations.shape[0])

    if min_read_s>=min_read:
        min_idx = my_recommendations["rating_count"]>=min_read_s
    else:
        min_idx = np.repeat(True, my_recommendations.shape[0])

    if max_read_s<=max_read:
        max_idx = my_recommendations["rating_count"]<+max_read_s
    else:
        max_idx = np.repeat(True, my_recommendations.shape[0])

    
    displayed = my_recommendations[selected_idx&(~filtered_idx)&min_idx&max_idx]

    if selected_user=='Orsi':
        target_col = 'bosolya_rating'
    else:
        target_col = 'vtisza_rating'

    if is_recommended=="Ajanlott":
        displayed = displayed.sort_values(target_col,ascending=False).reset_index(drop=True)[['author','title', 'book_tags', 'url']][:1000]
    else:
        displayed = displayed.sort_values(target_col,ascending=True).reset_index(drop=True)[['author','title', 'book_tags', 'url']][:1000]
    
    displayed.index = displayed.index+1

    st.write(displayed.to_html(escape=False), unsafe_allow_html=True)