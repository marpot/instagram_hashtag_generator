import streamlit as st
import pandas as pd
import json
import plotly.express as px
from bs4 import BeautifulSoup
import requests

st.title('Instagram Hashtag Analysis')

def get_count(tag):
    url = f"https://www.instagram.com/explore/tags/{tag}/"
    try:
        s = requests.get(url)
        soup = BeautifulSoup(s.content, 'html.parser')
        return int(soup.find_all("meta")[6]["content"].split(" ")[0].replace("K", "000").replace("B", "000000000").replace("M", "000000").replace(".", ""))
    except Exception as e:
        st.error(f"Error fetching count for {tag}: {str(e)}")
        return 0

def get_best(tag, topn):
    url = f"https://best-hashtags.com/hashtag/{tag}/"
    try:
        s = requests.get(url)
        soup = BeautifulSoup(s.content, 'html.parser')
        tags = soup.find("div", {"class": "tag-box tag-box-v3 margin-bottom-40"}).text.split()[:topn]
        tags = [tag for tag in tags]
        return tags
    except Exception as e:
        st.error(f"Error fetching best hashtags for {tag}: {str(e)}")
        return []

def save_data(data):
    with open("database.json", "w") as f:
        json.dump(data, f, indent=4)

def load_data():
    try:
        with open("database.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {"hashtag_data": {}}  # Return an empty dictionary if the file doesn't exist
    return data

data = load_data()
num_tags = st.sidebar.number_input("Select number of tags", 1, 30)

st.sidebar.header("Tags")
col1, col2 = st.sidebar.columns(2)

tags = []
sizes = []
for i in range(num_tags):
    tag = col1.text_input(f"Tag {i}", key=f"tag_{i}")
    size = col2.number_input(f"Top-N {i}", 1, 10, key=f"size_{i}")
    tags.append(tag)
    sizes.append(size)
    
# only execute if the `Create Hashtags` button is pressed
if st.sidebar.button("Create Hashtags"):
    tab_names = ["all"] + tags
    tag_tabs = st.tabs(tab_names)

    all_hashtags = []
    hashtag_data = []

    for i in range(num_tags):
        hashtags = get_best(tags[i], sizes[i])
        for hashtag in hashtags:
            if hashtag in data["hashtag_data"]:
                hashtag_count = data["hashtag_data"][hashtag]
            else:
                hashtag_count = get_count(hashtag.replace("#", ""))
                data["hashtag_data"][hashtag] = hashtag_count
            hashtag_data.append((f"{hashtag}<br>{hashtag_count:,}", hashtag_count))

        tag_tabs[i+1].text_area(f"Tags for {tags[i]}", " ".join(hashtags))
        all_hashtags = all_hashtags + hashtags

    tag_tabs[0].text_area("All Hashtags", " ".join(all_hashtags))

    st.header("Hashtag Count Data")
    df = pd.DataFrame(hashtag_data, columns=["hashtag", "count"])
    df = df.sort_values("count")

    save_data(data)  # Save data only once after analysis is complete

    fig = px.bar(df, x='hashtag', y='count')
    st.plotly_chart(fig, use_container_width=True)