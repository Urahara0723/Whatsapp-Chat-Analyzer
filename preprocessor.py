import pandas as pd
import re

def preprocess(data):

    # Fix unicode space issue
    data = data.replace('\u202f', ' ')

    # Pattern for WhatsApp messages
    pattern = r'(\d{2}/\d{2}/\d{4},\s\d{1,2}:\d{2}\s[ap]m)\s-\s'

    # Split messages and dates
    message_list = re.split(pattern, data)[1:]

    dates = message_list[::2]
    messages = message_list[1::2]

    users = []
    user_messages = []

    for message in messages:

        # Split only on first colon
        entry = re.split(r'([^:]+):\s', message, maxsplit=1)

        if len(entry) >= 3:
            users.append(entry[1])
            user_messages.append(entry[2])

        else:
            users.append('group_notification')
            user_messages.append(message)

    # Create dataframe
    df = pd.DataFrame({
        'user_name': users,
        'user_message': user_messages,
        'message_dates': dates
    })
    
    df = df[df['user_name'] != 'group_notification']
    # Convert dates
    df['message_dates'] = df['message_dates'].str.upper()

    df['date'] = pd.to_datetime(
        df['message_dates'],
        format='%d/%m/%Y, %I:%M %p'
    )

    df.drop(columns=['message_dates'], inplace=True)

    # Extra features
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute
    df['month_num'] = df['date'].dt.month

    period = []

    for hour in df['hour']:

        start = pd.to_datetime(hour, format='%H').strftime('%I %p')
        end = pd.to_datetime((hour + 1) % 24, format='%H').strftime('%I %p')

        period.append(f'{start} - {end}')

    df['period'] = period

    return df