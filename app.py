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
    'lang': 'en',
    'personalization_id': '"v1_QkUMFFmmbdywcvuDnDcUJg=="',
}

headers = {
    'accept': '*/*',
    'accept-language': 'en-IN,en;q=0.9,kn-IN;q=0.8,kn;q=0.7,en-GB;q=0.6,en-US;q=0.5',
    'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
    'content-type': 'application/json',
    # 'cookie': 'lang=en; guest_id=v1%3A172232719896812909; night_mode=2; guest_id_marketing=v1%3A172232719896812909; guest_id_ads=v1%3A172232719896812909; g_state={"i_l":0}; kdt=byTzgcmFQJyDztaJSOfAewSbJxJ2TUwUEJ7Dzi96; auth_token=1060e18f293825c03663ec7578f0a2bce1b43986; ct0=202ebc70c7ef2186d8c4c77afd0610833495affee2b23fec4a6e83b9d6e447dcdad9e82e84b10fdc69bdbcbe50875a4bbae5401f3177a11f3becc589bf269443bea0c0617dc705697e46ae50d3587599; twid=u%3D1738539837852905472; lang=en; personalization_id="v1_QkUMFFmmbdywcvuDnDcUJg=="',
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

time.sleep(3)

def extract_tweet_data(data):
    # Your existing logic to extract tweets
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
                        utc_zone = pytz.utc
                        ist_zone = pytz.timezone('Asia/Kolkata')
                        created_at_utc = utc_zone.localize(created_at_datetime)
                        created_at_ist = created_at_utc.astimezone(ist_zone)
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


def save_to_csv(data_list, filename='twitterdata.csv'):
    keys = data_list[0].keys()
    with open(filename, 'a', newline='', encoding='utf-8') as output_file:  # Change to 'a' for append
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        if output_file.tell() == 0:  # Write header only if file is empty
            dict_writer.writeheader()
        dict_writer.writerows(data_list)
    print(f"Data appended to {filename}")


def get_bottom_cursor_value(json_response):
    entries = json_response.get("data", {}).get("user", {}).get("result", {}).get("timeline_v2", {}).get("timeline", {}).get("instructions", [])
    
    for instruction in entries:
        if instruction.get("type") == "TimelineAddEntries":
            for entry in instruction.get("entries", []):
                if entry.get("content", {}).get("cursorType") == "Bottom":
                    return entry["content"]["value"]

    return None

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
        if isinstance(end_date, str):
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            end_date_obj = end_date.date()
        adjusted_end_date = end_date_obj - timedelta(days=1)
        print(adjusted_end_date)

        for tweet in extracted_data_list:
            created_at_str = tweet['created_at_ist']  # This is a string in your specified format

            # Convert created_at from string to datetime and extract the date
            created_at_date = datetime.strptime(created_at_str, '%Y-%m-%d %H:%M:%S').date()

            # Check if created_at_date is less than end_date_obj
            if created_at_date < adjusted_end_date:  
                print("Reached end date. Exiting...")
                
                return [], None
        # After the loop
        bottom_cursor_value = get_bottom_cursor_value(response_data)
        return extracted_data_list, bottom_cursor_value
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        return [], None




@app.route('/')
def index():
    return render_template('index.html')




@app.route('/scrape', methods=['POST'])
async def scrape():  # Make this function async
    data = request.get_json()
    url = data['url']
    end_date = data['end_date']

    # Extract username from URL
    match = re.search(r'https?://x\.com/([^/]+)', url)
    username = match.group(1) if match else None

    # Get user profile
    params = {'variables': f'{{"screen_name":"{username}"}}'}
    response_profile = requests.get(
        'https://x.com/i/api/graphql/-0XdHI-mrHWBQd8-oLo1aA/ProfileSpotlightsQuery',
        params=params,
        cookies=cookies,
        headers=headers,
    )

    # Error handling for profile response
    if response_profile.status_code != 200:
        return jsonify({"error": "Failed to fetch user profile"}), 400
    
    data = response_profile.json()
    rest_id = data['data']['user_result_by_screen_name']['result']['rest_id']
    all_extracted_data = []
    cursor = None

    while True:
        extracted_data, cursor = await fetch_tweets(rest_id, end_date, cursor)  # Await here

        if not extracted_data or cursor is None:
            break

        save_to_csv(extracted_data)
        all_extracted_data.extend(extracted_data)

    return jsonify(all_extracted_data)

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




