from flask import Flask, request, jsonify
import requests
import random
import time
import json
from bs4 import BeautifulSoup
import os
import sys
import warnings
from datetime import datetime

warnings.filterwarnings('ignore')

app = Flask(__name__)

# Helper functions as defined in your original code
def get_dict(soup1):
    # Initialize the dictionary to hold extracted data
    inner_dict = {}

    # Extract title
    try:
        title_div = soup1.find('div', class_='document-content')
        title = title_div.find('h1').get_text(strip=True) if title_div else None
    except Exception as e:
        print(f"Error extracting title.")
        title = None

    try:
        sum_div = soup1.find('div', class_='document-summary group')
        summary = sum_div.get_text()
    except:
        summary = ''
    # Extract metadata
    try:
        metadata_dl = soup1.find('dl', class_='group')
        data = {}
        if metadata_dl:
            for dt in metadata_dl.find_all('dt'):
                label = dt.get_text(strip=True).replace(':', '')
                dd = dt.find_next_sibling('dd')
                if dd:
                    if dd.find('time'):
                        data[label] = dd.find('time').get_text(strip=True)
                    else:
                        data[label] = dd.get_text(strip=True)
        else:
            data = {}
    except Exception as e:
        print(f"Error extracting metadata.")
        data = {}

    # Extract document link
    try:
        document_div = soup1.find('div', class_='document-file group')
        if document_div:
            links = document_div.find_all('a')
            d_link = links[0].get('href') if links else None
        else:
            d_link = None
    except Exception as e:
        print(f"Error extracting document link.")
        d_link = None

    # Populate the final dictionary
    inner_dict['Page title'] = title
    inner_dict['More information'] = data
    inner_dict['Document Link'] = d_link
    inner_dict['Summary'] = summary

    return inner_dict


def compare_and_update(dict1, dict2):
    if not dict1:
        return 'no', dict2

    u = dict1.get('main url', '')
    v = dict2.get('main url', '')
    status = 'no'

    if u == v:
        data1 = dict1.get('main data', [])
        data2 = dict2.get('main data', [])
        dict1_dates = {
            (item.get('Page title', ''), item.get('url', '')): item.get('More information', {}).get('Page updated', '')
            for item in data1
            if all(key in item for key in ['Page title', 'url', 'More information'])
        }

        for item in data2:
            key = (item.get('Page title', ''), item.get('url', ''))
            if key in dict1_dates:
                try:
                    date1 = datetime.strptime(dict1_dates[key], '%d %B %Y')
                    date2 = datetime.strptime(item.get('More information', {}).get('Page updated', ''), '%d %B %Y')
                    item['update information'] = 'Updated' if date2 > date1 else 'Not updated'
                except ValueError:
                    item['update information'] = 'Date format error'
                except TypeError:
                    item['update information'] = 'Missing date information'
            else:
                item['update information'] = None

        status = 'yes'
    else:
        print(f"URLs do not match: {u} != {v}")

    return status, dict2


user_agent_list = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
]

# Define API routes
@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({"error": "URL is required"}), 400

    if url.endswith('/'):
        file_name = url.split('/')[-2]
    else:
        url = f'{url}/'
        file_name = url.split('/')[-2]

    try:
        with open(f'{file_name}.json', 'r') as file:
            dict1 = json.load(file)
            print("Successfully read previous JSON file.")
    except (FileNotFoundError, json.JSONDecodeError):
        dict1 = {}

    try:
        res = requests.get(url, headers={'User-Agent': random.choice(user_agent_list)})

        if res.status_code == 200:
            soup = BeautifulSoup(res.content, 'html.parser')
            a = soup.find('article', class_='rich-text').find_all('ul')
            links_1 = [li.find('a').get('href') for ul in a for li in ul.find_all('li') if 'https' in li.find('a').get('href')]

            if links_1:
                all_dicts = []

                for link in links_1[:2]:
                    try:
                        res1 = requests.get(link, headers={'User-Agent': random.choice(user_agent_list)})

                        if res1.status_code == 200:
                            soup1 = BeautifulSoup(res1.content, 'html.parser')
                            z = get_dict(soup1)
                            z['url'] = link
                            z['update information'] = None
                            z['scraped time'] = datetime.now().strftime('%Y-%m-%d %H_%M_%S')
                            all_dicts.append(z)
                        else:
                            print(f'Error {res1.status_code} for the URL {link}')
                    except requests.RequestException as e:
                        print(f'Request exception for URL {link}: {e}')
                dict2 = {'main url': url, 'main data': all_dicts}

                r, updated_dict2 = compare_and_update(dict1, dict2)

                # Save the data to the file
                with open(f'{file_name}.json', 'w') as file:
                    json.dump(updated_dict2, file, indent=3)

                return jsonify(updated_dict2), 200
            else:
                return jsonify({"error": "No inner links found"}), 400
        else:
            return jsonify({"error": f"Error while sending request: {res.status_code}"}), 500
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
