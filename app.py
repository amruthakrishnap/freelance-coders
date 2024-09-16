from flask import Flask, request, jsonify
import requests
import random
import json
from bs4 import BeautifulSoup
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

app = Flask(__name__)

# Define the user agent list
user_agent_list = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
]

# Helper functions as defined in your original code
def get_dict(soup1):
    inner_dict = {}
    try:
        title_div = soup1.find('div', class_='document-content')
        title = title_div.find('h1').get_text(strip=True) if title_div else None
    except Exception:
        title = None

    try:
        sum_div = soup1.find('div', class_='document-summary group')
        summary = sum_div.get_text()
    except:
        summary = ''

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
    except Exception:
        data = {}

    try:
        document_div = soup1.find('div', class_='document-file group')
        if document_div:
            links = document_div.find_all('a')
            d_link = links[0].get('href') if links else None
        else:
            d_link = None
    except Exception:
        d_link = None

    inner_dict['Page title'] = title
    inner_dict['More information'] = data
    inner_dict['Document Link'] = d_link
    inner_dict['Summary'] = summary

    return inner_dict

@app.route('/')
def hello_world():
    return 'Hello World!', 200

@app.route('/scrape', methods=['POST'])
def scrape():
    try:
        # Ensure that the request contains JSON data
        if request.content_type != 'application/json':
            return jsonify({"error": "Content-Type must be application/json"}), 415
        
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({"error": "URL is required"}), 400

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
                        except requests.RequestException as e:
                            print(f'Request exception for URL {link}: {e}')
                    dict2 = {'main url': url, 'main data': all_dicts}
                    return jsonify(dict2), 200
                else:
                    return jsonify({"error": "No inner links found"}), 400
            else:
                return jsonify({"error": f"Error while sending request: {res.status_code}"}), 500
        except requests.RequestException as e:
            return jsonify({"error": str(e)}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
