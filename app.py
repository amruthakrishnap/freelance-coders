from flask import Flask, render_template, request, jsonify, send_file, make_response
import requests
import asyncio
import pandas as pd
import csv
from datetime import datetime, timedelta
import pytz
import re
import os
import time
import json
import io

app = Flask(__name__)

# Cookies and headers
cookies = {
    'lang': 'en',
    'guest_id': 'v1%3A172232719896812909',
    'night_mode': '2',
    'guest_id_marketing': 'v1%3A172232719896812909',
    'guest_id_ads': 'v1%3A172232719896812909',
    'g_state': '{"i_l":0}',
    'kdt': 'byTzgcmFQJyDztaJSOfAewSbJxJ2TUwUEJ7Dzi96',
    'auth_token': '1060e18f293825c03663ec7578f0a2bce1b43986',
    'ct0': '202ebc70c7ef2186d8c4c77afd0610833495affee2b23fec4a6e83b9d6e447dcdad9e82e84b10fdc69bdbcbe50875a4bbae5401f3177a11f3becc589bf269443bea0c0617dc705697e46ae50d3587599',
    'twid': 'u%3D1738539837852905472',
    'personalization_id': '"v1_QkUMFFmmbdywcvuDnDcUJg=="',
}

headers = {
    'accept': '*/*',
    'accept-language': 'en-IN,en;q=0.9,kn-IN;q=0.8,kn;q=0.7,en-GB;q=0.6,en-US;q=0.5',
    'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
    'content-type': 'application/json',
    'priority': 'u=1, i',
    'referer': 'https://x.com/narendramodi',
    'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    'x-client-transaction-id': 'FO8hX00FvQJMKxcK+ACkpuuFdleebUzDHf1RBTM8yUiKdY8j2XhfPE8Z8FKg90wBFhP9sRbAW4kIqYxRR0ynUwdx1QXlFw',
    'x-client-uuid': '9ca5d2e3-056a-4f01-815b-22a1c4ab1dc3',
    'x-csrf-token': '202ebc70c7ef2186d8c4c77afd0610833495affee2b23fec4a6e83b9d6e447dcdad9e82e84b10fdc69bdbcbe50875a4bbae5401f3177a11f3becc589bf269443bea0c0617dc705697e46ae50d3587599',
    'x-twitter-active-user': 'yes',
    'x-twitter-auth-type': 'OAuth2Session',
    'x-twitter-client-language': 'en',
}

# Function to extract tweet data
def extract_tweet_data(data):
    all_extracted_data = []
    try:
        instructions = data['data']['user']['result']['timeline_v2']['timeline']['instructions']
        for instruction in instructions:
            if instruction.get('entries'):
                for entry in instruction['entries']:
                    content = entry.get('content', {})
                    item_content = content.get('itemContent', {})
                    tweet_results = item_content.get('tweet_results', {})
                    tweet_data = tweet_results.get('result', {})
                    if 'legacy' in tweet_data:
                        created_at_utc = tweet_data['legacy']['created_at']
                        created_at_datetime = datetime.strptime(created_at_utc, "%a %b %d %H:%M:%S +0000 %Y")
                        created_at_ist = pytz.utc.localize(created_at_datetime).astimezone(pytz.timezone('Asia/Kolkata'))
                        created_at_ist_str = created_at_ist.strftime("%Y-%m-%d %H:%M:%S")

                        rest_id = tweet_data['rest_id']
                        user_data = tweet_data.get('core', {}).get('user_results', {}).get('result', {})
                        screen_name = user_data.get('legacy', {}).get('screen_name', 'N/A')
                        views_count = tweet_data.get('views', {}).get('count', 'N/A')
                        full_text = tweet_data['legacy']['full_text'].replace("\n\n", " ")
                        quote_count = tweet_data['legacy']['quote_count']
                        reply_count = tweet_data['legacy']['reply_count']
                        retweet_count = tweet_data['legacy']['retweet_count']
                        favorite_count = tweet_data['legacy']['favorite_count']
                        tweet_url = f"https://x.com/{screen_name}/status/{rest_id}"

                        extracted_data = {
                            'created_at_ist': created_at_ist_str,
                            'Tweet_Url': tweet_url,
                            'full_text': full_text,
                            'views_count': views_count,
                            'quote_count': quote_count,
                            'reply_count': reply_count,
                            'retweet_count': retweet_count,
                            'favorite_count': favorite_count
                        }
                        all_extracted_data.append(extracted_data)
                    else:
                        print("Skipping tweet with missing 'legacy' key.")
    except KeyError as e:
        print(f"KeyError: {e} - The JSON structure might have changed.")
        return []

    return all_extracted_data

# Asynchronous function to fetch tweets
async def fetch_tweets(rest_id, end_date, cursor=None):
    params = {
        'variables': f'{{"userId":"{rest_id}","count":20,"includePromotedContent":true,"withQuickPromoteEligibilityTweetFields":true,"withVoice":true,"withV2Timeline":true,"cursor":"{cursor or ""}"}}',
        'features': '{"rweb_tipjar_consumption_enabled":true,"responsive_web_graphql_exclude_directive_enabled":true,"verified_phone_label_enabled":true,"creator_subscriptions_tweet_preview_api_enabled":true,"responsive_web_graphql_timeline_navigation_enabled":true,"responsive_web_graphql_skip_user_profile_image_extensions_enabled":false,"communities_web_enable_tweet_community_results_fetch":true,"c9s_tweet_anatomy_moderator_badge_enabled":true,"articles_preview_enabled":true,"responsive_web_edit_tweet_api_enabled":true,"graphql_is_translatable_rweb_tweet_is_translatable_enabled":true,"view_counts_everywhere_api_enabled":true,"longform_notetweets_consumption_enabled":true,"responsive_web_twitter_article_tweet_consumption_enabled":true,"tweet_awards_web_tipping_enabled":false,"creator_subscriptions_quote_tweet_preview_enabled":false,"freedom_of_speech_not_reach_fetch_enabled":true,"standardized_nudges_misinfo":true,"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":true,"rweb_video_timestamps_enabled":true,"longform_notetweets_rich_text_read_enabled":true,"longform_notetweets_inline_media_enabled":true,"responsive_web_enhance_cards_enabled":false}',
        'fieldToggles': '{"withArticlePlainText":false}',
    }

    response = requests.get(
        'https://x.com/i/api/graphql/E3opETHurmVJflFsUBVuUQ/UserTweets',
        params=params,
        cookies=cookies,
        headers=headers,
    )

    if response.status_code == 200:
        response_data = response.json()
        extracted_data_list = extract_tweet_data(response_data)
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date() if isinstance(end_date, str) else end_date.date()
        adjusted_end_date = end_date_obj - timedelta(days=1)

        for tweet in extracted_data_list:
            created_at_str = tweet['created_at_ist']
            created_at_date = datetime.strptime(created_at_str, '%Y-%m-%d %H:%M:%S').date()

            if created_at_date < adjusted_end_date:  
                print("Reached end date. Exiting...")
                return extracted_data_list, None

        bottom_cursor_value = get_bottom_cursor_value(response_data)
        return extracted_data_list, bottom_cursor_value
    else:
        print(f"Error: {response.status_code}")
        return [], None

# Helper function to get bottom cursor value
def get_bottom_cursor_value(data):
    try:
        instructions = data['data']['user']['result']['timeline_v2']['timeline']['instructions']
        for instruction in instructions:
            if instruction.get('entries'):
                entries = instruction['entries']
                if entries:
                    return entries[-1]['content']['operation']['cursor']['value']
    except KeyError as e:
        print(f"KeyError: {e} - The JSON structure might have changed.")
    return None

# Asynchronous function to fetch all tweets
async def fetch_all_tweets(rest_id, end_date):
    all_tweets = []
    cursor = None

    while True:
        tweets, cursor = await fetch_tweets(rest_id, end_date, cursor)
        if not tweets:
            break
        all_tweets.extend(tweets)

        if not cursor:
            break

    return all_tweets

# Route to handle tweet fetching
@app.route('/fetch_tweets', methods=['POST'])
async def fetch_tweets_route():
    data = request.get_json()
    rest_id = data.get('rest_id')
    end_date = data.get('end_date')

    if not rest_id or not end_date:
        return jsonify({"error": "rest_id and end_date are required."}), 400

    all_tweets = await fetch_all_tweets(rest_id, end_date)
    return jsonify(all_tweets)

# Route to download tweets as CSV
@app.route('/download_tweets', methods=['POST'])
def download_tweets():
    data = request.get_json()
    tweets = data.get('tweets')

    if not tweets:
        return jsonify({"error": "No tweets to download."}), 400

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(tweets[0].keys())  # Write header

    for tweet in tweets:
        writer.writerow(tweet.values())

    output.seek(0)
    return send_file(output, mimetype='text/csv', as_attachment=True, download_name='tweets.csv')

if __name__ == '__main__':
    app.run(debug=True)
