import streamlit as st
import zipfile
import os
import preprocessor
import helper
import matplotlib.pyplot as plt
import squarify
import pandas as pd


st.title("Whatsapp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Upload WhatsApp Zip File")

if uploaded_file is not None:

    # Save uploaded zip temporarily
    with open("chat.zip", "wb") as f:
        f.write(uploaded_file.getbuffer())

    
    # Extract zip and create folder if not exists
if not os.path.exists("chat_data"):
    os.makedirs("chat_data")

# Delete old files
for file in os.listdir("chat_data"):
    os.remove(os.path.join("chat_data", file))

# Extract new zip
with zipfile.ZipFile("chat.zip", 'r') as zip_ref:
    zip_ref.extractall("chat_data")

    # Find txt file
    txt_file = None

    for file in os.listdir("chat_data"):
        if file.endswith(".txt"):
            txt_file = file
            break

    # Read txt file
    with open(f"chat_data/{txt_file}", 'r', encoding='utf-8') as f:
        data = f.read()

    # Preprocess
    df = preprocessor.preprocess(data)

    # Display dataframe
    st.dataframe(df)

    user_list = df['user_name'].unique().tolist()
    

    user_list.insert(0, "Overall")

    selected_user = selected_user = st.sidebar.selectbox(
    "Show analysis wrt",
    user_list
    )

    if st.sidebar.button("Show_analysis"):

        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header('Total Messages:')
            st.title(num_messages)
        with col2:
            st.header('Total Words')
            st.title(words)
        with col3:
            st.header('Media Shared')
            st.title(num_media_messages)
        with col4:
            st.header('Links Shared')
            st.title(num_links)

        # Finding the busiest users in the group
        if selected_user == 'Overall':
            st.title('Most Busy users')
            x, new_df = helper.most_busy_users(df)
            fig, ax = plt.subplots()
            col1, col2 = st.columns(2)

            with col1:
                ax.barh(x.index, x.values, color='skyblue')

                ax.set_xlabel("Messages")
                ax.set_ylabel("Users")
                ax.set_title("Message Count by Users")

                # Remove unnecessary borders
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)

                # Add values beside bars
                for i, v in enumerate(x.values):
                   ax.text(v + 10, i, str(v), va='center')

                st.pyplot(fig)

            with col2:
                st.dataframe(new_df)

            # Most common words 

        st.title("Most Common Words")

        common_df = helper.most_common_words(selected_user, df)

        fig, ax = plt.subplots(figsize=(12, 6))

        labels = [
               f"{word}\n({count})"
               for word, count in zip(common_df[0], common_df[1])
        ]

        squarify.plot(
                sizes=common_df[1],
                label=labels,
                alpha=0.8,
                pad=True,
                ax=ax
        )

        plt.axis('off')

        st.pyplot(fig)  

        # emoji analysis

        emoji_df = helper.emoji_helper(selected_user, df)
        st.title("Emoji Analysis")  
        st.dataframe(emoji_df) 

        # Monthly Timeline

        st.title("Monthly Timeline")

        timeline = helper.monthly_timeline(selected_user, df)

        fig, ax = plt.subplots(figsize=(12,5))

        ax.plot(timeline['time'], timeline['user_message'], color='green', marker='o')

        plt.xticks(rotation='vertical')

        ax.set_xlabel("Month")
        ax.set_ylabel("Messages")

        st.pyplot(fig)  

        # Reply time

        st.title("Reply Time Analysis")

        reply_data = helper.reply_time_analysis(df)

        reply_df = pd.DataFrame(
            list(reply_data.items()),
            columns=['User', 'Average Reply Time (min)']
        )

        st.dataframe(reply_df)

        st.title("Conversation Starter Analysis")

        starter_data = helper.conversation_starter(df)

        starter_df = pd.DataFrame(
            list(starter_data.items()),
            columns=['User', 'Conversation Starts']
        )

        st.dataframe(starter_df)

        total = starter_df['Conversation Starts'].sum()

        for _, row in starter_df.iterrows():

            percent = round(
                (row['Conversation Starts'] / total) * 100,
                2
            )

            st.write(
                f"{row['User']} initiated {percent}% of conversations."
            )

    st.title("Most Active Time of Day")

    active_df = helper.most_active_time(selected_user, df)

    fig, ax = plt.subplots(figsize=(12,5))

    ax.plot(
       active_df['time_period'],
       active_df['message_count'],
       marker='o'
    )

    plt.xticks(rotation='vertical')

    ax.set_xlabel("Time Period")
    ax.set_ylabel("Messages")
    ax.set_title("Chat Activity by Time")

    st.pyplot(fig)
        
    peak_time = active_df.iloc[0]['time_period']

    st.success(f"Most active chatting time: {peak_time}")

    st.title("Chat Personality Analyzer")

    personality_data = helper.personality_analysis(df)

    for user, traits in personality_data.items():

        st.subheader(f"🧠 {user}")

        for trait in traits:

            st.markdown(f"- {trait}")

        st.divider()

    