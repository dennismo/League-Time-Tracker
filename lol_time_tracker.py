from functools import reduce
from datetime import datetime, timedelta
import pytz
import sys
import requests, bs4, re, time

import plotly.graph_objects as go

API_KEY = "RGAPI-14e60e4c-822c-4ec4-93ff-371cf3c846a6"
HEADER = {
    "Origin": "https://developer.riotgames.com",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Riot-Token": API_KEY,
    "Accept-Language": "en-us",
    "User-Agent": ""
}


def get_account_id(user_name):
    response = requests.get('https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/' + user_name,
                            headers=HEADER)
    if response.status_code != 200:
        raise Exception("Cannot get accountID via API")
    return response.json()['accountId']


def get_match_ids(beginTime_stamp, accountId):
    beginTime = str("{:.3f}".format(beginTime_stamp)).replace(".", "")
    response = requests.get(
        'https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/' + accountId,
        params={
            "beginTime": beginTime,
        },
        headers=HEADER)
    if response.status_code != 200:
        raise Exception("API call did not go through")
    match_list = response.json()["matches"]
    match_ids = [match['gameId'] for match in match_list]
    return match_ids


def get_matches_data(match_ids):
    resp = dict()
    for match_id in match_ids:
        resp[match_id] = requests.get("https://na1.api.riotgames.com/lol/match/v4/matches/" + str(match_id),
                                      headers=HEADER)

    matches_data = {match_id: match.json() for match_id, match in resp.items()}
    return matches_data


def get_time_dict(matches_data, beginTime_stamp):
    time_data = {}

    cur_time = tz.localize(datetime.fromtimestamp(beginTime_stamp))
    today_pt = local_now

    while cur_time <= local_now + timedelta(hours=1):
        cur_pt = cur_time.strftime("%Y/%m/%d")
        time_data[cur_pt] = 0
        cur_time += timedelta(days=1)

    for match_id, match in matches_data.items():
        try:
            cur_pt = datetime.fromtimestamp(match['gameCreation'] / 1000).strftime("%Y/%m/%d")
            time_data[cur_pt] += match['gameDuration'] / 3600
        except:
            print(match)

    for time, duration in time_data.items():
        time_data[time] = str("{:.2f}".format(duration))

    return time_data


def transform_data(time_data):
    total_time_x = []
    total_time_list = []

    for date, total_time in sorted(time_data.items()):
        total_time_x.append(date)
        total_time_list.append(total_time)
    return total_time_x, total_time_list


def render_data(total_time_x, total_time_list, userName, days):
    fig = go.Figure(data=go.Bar(x=total_time_x, y=total_time_list, text=total_time_list,
                                textposition='auto', ))
    fig.update_layout(
        title='Amount of Hours "' + userName + '" Spends on League of Legends in the past ' + str(days) + ' days',
        xaxis_tickfont_size=14,
        yaxis=dict(
            title='Hours',
            titlefont_size=16,
            tickfont_size=14,
        ),
    )
    fig.write_html('stellar_lol_time_tracking.html', auto_open=True)


if __name__ == '__main__':
    try:
        user_name = str(sys.argv[1])
        days = int(sys.argv[2])
    except Exception as e:
        print(e)
        sys.exit(2)

    now = datetime.now()
    tz = pytz.timezone("America/New_York")
    local_now = tz.localize(now)
    beginTime_stamp = datetime.timestamp(local_now - timedelta(days=days))
    print(beginTime_stamp)

    accountId = get_account_id(user_name)
    match_ids = get_match_ids(beginTime_stamp, accountId)
    matches_data = get_matches_data(match_ids)
    print(matches_data)
    time_data = get_time_dict(matches_data, beginTime_stamp)
    print(time_data)
    total_time_x, total_time_list = transform_data(time_data)
    render_data(total_time_x, total_time_list, user_name, days)
