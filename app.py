from flask import Flask, render_template, request, jsonify,make_response
import requests
import asyncio
import csv
from datetime import datetime, timedelta
import pytz
import re
import time
app = Flask(__name__)
import io
import json

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
    'external_referer': 'Jp2T2u05mcLwFRlJyxLNFhCN8nVxPuil|0|8e8t2xd8A2w%3D',
    'lang': 'en',
    'personalization_id': '"v1_j/GGO6YMHTTcXlBqjj7vDw=="',
}

headers = {
    'accept': '*/*',
    'accept-language': 'en-IN,en;q=0.9,kn-IN;q=0.8,kn;q=0.7,en-GB;q=0.6,en-US;q=0.5',
    'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
    'content-type': 'application/json',
    # 'cookie': 'lang=en; guest_id=v1%3A172232719896812909; night_mode=2; guest_id_marketing=v1%3A172232719896812909; guest_id_ads=v1%3A172232719896812909; g_state={"i_l":0}; kdt=byTzgcmFQJyDztaJSOfAewSbJxJ2TUwUEJ7Dzi96; auth_token=1060e18f293825c03663ec7578f0a2bce1b43986; ct0=202ebc70c7ef2186d8c4c77afd0610833495affee2b23fec4a6e83b9d6e447dcdad9e82e84b10fdc69bdbcbe50875a4bbae5401f3177a11f3becc589bf269443bea0c0617dc705697e46ae50d3587599; twid=u%3D1738539837852905472; external_referer=Jp2T2u05mcLwFRlJyxLNFhCN8nVxPuil|0|8e8t2xd8A2w%3D; lang=en; personalization_id="v1_j/GGO6YMHTTcXlBqjj7vDw=="',
    'priority': 'u=1, i',
    'referer': 'https://x.com/search?q=%28from%3Anarendramodi%29+until%3A2024-09-28+since%3A2024-09-20&src=typed_query&f=live',
    'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    'x-client-transaction-id': 'Sd3kEU6bOYtKaGUeSC1aaETQaiGfVEGGY0bcUsKPQ37Yhq2dzLcF1fFNdGqf5J/QUp8j7kuv2dWY/7skrlxRVBrrQ6hISg',
    'x-client-uuid': '9ca5d2e3-056a-4f01-815b-22a1c4ab1dc3',
    'x-csrf-token': '202ebc70c7ef2186d8c4c77afd0610833495affee2b23fec4a6e83b9d6e447dcdad9e82e84b10fdc69bdbcbe50875a4bbae5401f3177a11f3becc589bf269443bea0c0617dc705697e46ae50d3587599',
    'x-twitter-active-user': 'yes',
    'x-twitter-auth-type': 'OAuth2Session',
    'x-twitter-client-language': 'en',
}

# response = requests.get(
#     url,
#     cookies=cookies,
#     headers=headers,
# )

def get_bottom_cursor(data):
    bottom_cursor_value = None
    instructions = data.get("data", {}).get("search_by_raw_query", {}).get("search_timeline", {}).get("timeline", {}).get("instructions", [])

    for instruction in instructions:
        if instruction.get("type") in ["TimelineAddEntries", "TimelineReplaceEntry"]:
            entries = instruction.get("entries", []) if instruction.get("type") == "TimelineAddEntries" else [instruction.get("entry", {})]
            for entry in entries:
                if entry.get("content", {}).get("__typename") == "TimelineTimelineCursor":
                    content = entry.get("content", {})
                    if content.get("cursorType") == "Bottom":
                        bottom_cursor_value = content.get("value")
                        break
            if bottom_cursor_value:
                break
    
    # if bottom_cursor_value:
        #  print("Bottom cursor value:", bottom_cursor_value)
    
    return bottom_cursor_value


def save_to_csv(data_list, filename='tweets_data.csv'):
    keys = data_list[0].keys()
    with open(filename, 'a', newline='', encoding='utf-8') as output_file:  # Change to 'a' for append
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        if output_file.tell() == 0:  # Write header only if file is empty
            dict_writer.writeheader()
        dict_writer.writerows(data_list)
    print(f"Data appended to {filename}")

from datetime import datetime
import pytz

def extract_tweet_data(data):
    all_extracted_data = []

    try:
        # Parse the instructions from the JSON
        instructions = data['data']['search_by_raw_query']['search_timeline']['timeline']['instructions']

        for instruction in instructions:
            if instruction.get('entries'):
                for entry in instruction['entries']:
                    content = entry.get('content', {})
                    item_content = content.get('itemContent', {})
                    tweet_results = item_content.get('tweet_results', {})
                    tweet_data = tweet_results.get('result', {})

                    if 'core' in tweet_data:
                        # Extract quoted tweet data if available
                        created_at_utc = tweet_data['legacy']['created_at']
                        created_at_datetime = datetime.strptime(created_at_utc, "%a %b %d %H:%M:%S +0000 %Y")
                        utc_zone = pytz.utc
                        ist_zone = pytz.timezone('Asia/Kolkata')
                        created_at_utc = utc_zone.localize(created_at_datetime)
                        created_at_ist = created_at_utc.astimezone(ist_zone)
                        created_at_ist_str = created_at_ist.strftime("%Y-%m-%d %H:%M:%S")
                        # Extract other data from the main tweet
                        rest_id = tweet_data['rest_id']
                        user_data = tweet_data.get('core', {}).get('user_results', {}).get('result', {})
                        screen_name = user_data.get('legacy', {}).get('screen_name', 'N/A')
                        views_count = tweet_data.get('views', {}).get('count', 'N/A')
                        full_text = tweet_data['legacy']['full_text'].replace("\n\n", " ")
                        quote_count = tweet_data['legacy'].get('quote_count', 0)
                        reply_count = tweet_data['legacy'].get('reply_count', 0)
                        retweet_count = tweet_data['legacy'].get('retweet_count', 0)
                        favorite_count = tweet_data['legacy'].get('favorite_count', 0)
                        tweet_url = f"https://x.com/{screen_name}/status/{rest_id}"

                        # Build extracted data
                        extracted_data = {
                            'quoted_created_at_ist': created_at_ist_str,  # Can be None if not available
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
                        print("Skipping tweet with missing 'core' key.")

    except KeyError as e:
        print(f"KeyError: {e} - The JSON structure might have changed.")
        return []

    return all_extracted_data




async def fetch_tweets(username, start_date_obj, adjusted_end_date, cursor):
    # Base URL
    base_url = 'https://x.com/i/api/graphql/UN1i3zUiCWa-6r-Uaho4fw/SearchTimeline?'
    variables = {
        "rawQuery": f"(from:{username}) until:{adjusted_end_date} since:{start_date_obj}",
        "count": 40,
        "querySource": "typed_query",
        "product": "Latest"
    }

    # Add cursor only if it is not None
    if cursor:
        variables["cursor"] = cursor

    # Construct the URL
    url = f"{base_url}variables={json.dumps(variables)}&features=%7B%22rweb_tipjar_consumption_enabled%22%3Atrue%2C%22responsive_web_graphql_exclude_directive_enabled%22%3Atrue%2C%22verified_phone_label_enabled%22%3Atrue%2C%22creator_subscriptions_tweet_preview_api_enabled%22%3Atrue%2C%22responsive_web_graphql_timeline_navigation_enabled%22%3Atrue%2C%22responsive_web_graphql_skip_user_profile_image_extensions_enabled%22%3Afalse%2C%22communities_web_enable_tweet_community_results_fetch%22%3Atrue%2C%22c9s_tweet_anatomy_moderator_badge_enabled%22%3Atrue%2C%22articles_preview_enabled%22%3Atrue%2C%22responsive_web_edit_tweet_api_enabled%22%3Atrue%2C%22graphql_is_translatable_rweb_tweet_is_translatable_enabled%22%3Atrue%2C%22view_counts_everywhere_api_enabled%22%3Atrue%2C%22longform_notetweets_consumption_enabled%22%3Atrue%2C%22responsive_web_twitter_article_tweet_consumption_enabled%22%3Atrue%2C%22tweet_awards_web_tipping_enabled%22%3Afalse%2C%22creator_subscriptions_quote_tweet_preview_enabled%22%3Afalse%2C%22freedom_of_speech_not_reach_fetch_enabled%22%3Atrue%2C%22standardized_nudges_misinfo%22%3Atrue%2C%22tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled%22%3Atrue%2C%22rweb_video_timestamps_enabled%22%3Atrue%2C%22longform_notetweets_rich_text_read_enabled%22%3Atrue%2C%22longform_notetweets_inline_media_enabled%22%3Atrue%2C%22responsive_web_enhance_cards_enabled%22%3Afalse%7D"
    response = requests.get(url, cookies=cookies, headers=headers)

    if response.status_code == 200:
        response_data = response.json()
        extracted_data_list = extract_tweet_data(response_data)

        bottom_cursor_value = get_bottom_cursor(response_data)
        time.sleep(5)
        # print(bottom_cursor_value)  # Debugging output
        return extracted_data_list, bottom_cursor_value
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        return [], None



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.get_json()  # Get the JSON data from the frontend
    url = data['url']
    end_date = data['end_date']
    start_date = data['start_date']

    # Parse the start and end dates
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
    
    # Adjust the end date by adding two days
    adjusted_end_date = end_date_obj + timedelta(days=2)

    # Extract the username from the URL
    match = re.search(r'https?://x\.com/([^/]+)', url)
    username = match.group(1) if match else None

    # Prepare to fetch user profile
    params = {
        'variables': '{"screen_name":"' + username + '"}',
    }

    response_profile = requests.get(
        'https://x.com/i/api/graphql/-0XdHI-mrHWBQd8-oLo1aA/ProfileSpotlightsQuery',
        params=params,
        cookies=cookies,  # Assuming you already have the cookies & headers
        headers=headers,
    )

    # Extract the rest_id from the response
    data = response_profile.json()
    rest_id = data['data']['user_result_by_screen_name']['result']['rest_id']

    all_extracted_data = []
    cursor = None

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Fetch tweets in a loop
    while True:
        extracted_data, cursor = loop.run_until_complete(fetch_tweets(username, start_date_obj.date(), adjusted_end_date, cursor))

        if not extracted_data or cursor is None:  # Stop if no data or cursor is None
            break
        
        save_to_csv(extracted_data)  # Save the extracted data
        all_extracted_data.extend(extracted_data)  # Collect all extracted data

        # Optional: Sleep to avoid hitting rate limits
        asyncio.sleep(1)

    return jsonify(all_extracted_data)  # Send the tweet data back as JSON



@app.route('/download-csv', methods=['POST'])
def download_csv():
    # Get the JSON data from the request (data that was displayed in the table)
    extracted_data = request.get_json()

    # Generate CSV from the tweet data
    si = io.StringIO()
    csv_writer = csv.DictWriter(si, fieldnames=extracted_data[0].keys())
    csv_writer.writeheader()
    csv_writer.writerows(extracted_data)
    
    # Create the response and attach the CSV
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=tweets_data.csv"
    output.headers["Content-type"] = "text/csv"
    return output



if __name__ == '__main__':
    app.run(debug=True)



