from urlextract import URLExtract
import matplotlib.pyplot as plt
extract = URLExtract()
from collections import Counter
import pandas as pd
import re
import emoji

def fetch_stats(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user_name'] == selected_user]

    # Fetching the number of messages
    num_messages = df.shape[0]

    # Fetching the total number of words
    words = []
    for message in df['user_message']:
        words.extend(message.split())

    # Fetching the number of media messages
    num_media_messages = df['user_message'].str.contains(
    '<Media omitted>',
    na=False
    ).sum()

    #Fetching the number of links shared
    links = []
    for message in df['user_message']:
        links.extend(extract.find_urls(message))

    return num_messages, len(words), num_media_messages, len(links)

def most_busy_users(df):
    x = df['user_name'].value_counts()
    df = round(
    (df['user_name'].value_counts() / df.shape[0]) * 100,
    2
    ).reset_index().rename(
    columns={
        'index': 'name',
        'user_name': 'percent'
    }
    )

    return x, df

def most_common_words(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user_name'] == selected_user]

    temp = df[df['user_name'] != 'group_notification']

    # Read stop words
    with open('stop_hinglish.txt', 'r') as f:
        stop_words = set(f.read().splitlines())

    words = []

    for message in temp['user_message']:

        message = message.lower()

        # Skip media messages
        if '<media omitted>' not in message:

            # Remove links
            message = re.sub(r'http\S+', '', message)

            # Remove punctuation/symbols/numbers
            message = re.sub(r'[^a-zA-Z\s]', '', message)

            for word in message.split():

                # Remove short useless words
                if (
                    word not in stop_words
                    and len(word) > 2
                ):

                    words.append(word)

    common_words = Counter(words).most_common(30)

    return pd.DataFrame(common_words)

def emoji_helper(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user_name'] == selected_user] 
  
    emojis = []
    for message in df['user_message']:
        emojis.extend([c for c in message if c in emoji.EMOJI_DATA])

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))

    return emoji_df

def monthly_timeline(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user_name'] == selected_user]

    timeline = df.groupby(
        ['year', 'month_num', 'month']
    ).count()['user_message'].reset_index()

    timeline = timeline.sort_values(['year', 'month_num'])

    time = []

    for i in range(timeline.shape[0]):
        time.append(
            timeline['month'].iloc[i] + "-" + str(timeline['year'].iloc[i])
        )

    timeline['time'] = time

    return timeline

def reply_time_analysis(df):

    df = df.sort_values('date')

    reply_times = {}

    previous_user = None
    previous_time = None

    for _, row in df.iterrows():

        current_user = row['user_name']
        current_time = row['date']

        if previous_user and current_user != previous_user:

            diff = (current_time - previous_time).total_seconds() / 60

            # Ignore huge gaps
            if diff < 1440:

                if current_user not in reply_times:
                    reply_times[current_user] = []

                reply_times[current_user].append(diff)

        previous_user = current_user
        previous_time = current_time

    avg_reply = {}

    for user, times in reply_times.items():

        avg_reply[user] = round(sum(times) / len(times), 2)

    return avg_reply

def conversation_starter(df):

    df = df.sort_values('date')

    starter_count = {}

    previous_time = None

    for _, row in df.iterrows():

        current_user = row['user_name']
        current_time = row['date']

        # First message
        if previous_time is None:

            starter_count[current_user] = starter_count.get(current_user, 0) + 1

        else:

            diff = (current_time - previous_time).total_seconds() / 3600

            # New conversation after 6 hours
            if diff > 6:

                starter_count[current_user] = starter_count.get(current_user, 0) + 1

        previous_time = current_time

    return starter_count

def most_active_time(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user_name'] == selected_user]

    active_time = df['period'].value_counts().reset_index()

    active_time.columns = ['time_period', 'message_count']

    return active_time

def personality_analysis(df):

    analysis = {}

    users = df['user_name'].unique()

    for user in users:

        temp = df[df['user_name'] == user]

        traits = []

        # Average words per message
        avg_words = temp['user_message'].apply(
            lambda x: len(x.split())
        ).mean()

        # Emoji usage
        emoji_count = temp['user_message'].str.count(
            r'[😀-🙏🤣😂❤️😭😍🥺🔥]'
        ).sum()

        # Night activity
        late_night_msgs = temp[
            (temp['hour'] >= 0) &
            (temp['hour'] <= 4)
        ].shape[0]

        # Message count
        total_msgs = temp.shape[0]

        # Consecutive messages
        consecutive = 0

        prev_user = None

        for current_user in df['user_name']:

            if current_user == prev_user == user:
                consecutive += 1

            prev_user = current_user

        # Traits

        # Expressiveness
        if avg_words > 20:
            traits.append("Overthinker 😄")

        elif avg_words > 10:
            traits.append("Expressive texter")

        elif avg_words < 4:
            traits.append("Dry texter 🥶")

        else:
            traits.append("Balanced texter")

        # Emoji personality
        if emoji_count > 100:
            traits.append("Emoji addict 😂")

        elif emoji_count > 30:
            traits.append("Emoji lover 😄")

        # Night owl
        if late_night_msgs > 50:
            traits.append("Night owl 🌙")

        # Double texting
        if consecutive > 30:
            traits.append("Double texter 📱")

        # Silent observer
        if total_msgs < df.shape[0] * 0.05:
            traits.append("Silent observer 👀")

        # Hyper active
        if total_msgs > df.shape[0] * 0.4:
            traits.append("Conversation carrier 🚀")

        analysis[user] = traits

    return analysis




