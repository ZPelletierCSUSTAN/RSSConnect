from flask import Flask, render_template, request, redirect, url_for, session, flash
import feedparser
import json
import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
app.secret_key = 'secure_key_change_this'

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DATA_FILE = os.path.join(DATA_DIR, 'user_data.json')

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# --- Constants ---
LIMIT_CATEGORIES = 50
LIMIT_FEEDS_PER_CAT = 30
FINDER_RESULT_LIMIT = 20

DEFAULT_CATEGORIES = [
    'World News', 'TV & Movies', 'Comics', 
    'Music', 'Video Games', 'Tech', 'Food', 'Other'
]

DEFAULT_FEEDS = [
    {'id': 'wn1', 'name': 'CNN', 'url': 'https://www.youtube.com/feeds/videos.xml?channel_id=UCupvZG-5ko_eiXAupbDfxWw', 'category': 'World News'},
    {'id': 'wn2', 'name': 'BBC News', 'url': 'https://www.youtube.com/feeds/videos.xml?channel_id=UC16niRr50-MSBwiO3YDb3RA', 'category': 'World News'},
    {'id': 'tc1', 'name': 'MKBHD', 'url': 'https://www.youtube.com/feeds/videos.xml?channel_id=UCBJycsmduvYEL83R_U4JriQ', 'category': 'Tech'},
]

# --- Helpers ---
def get_all_data():
    if not os.path.exists(DATA_FILE): return {}
    try:
        with open(DATA_FILE, 'r') as f:
            content = f.read().strip()
            return json.loads(content) if content else {}
    except: return {}

def save_all_data(data):
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except: pass

def get_user_config(username):
    all_data = get_all_data()
    user_data = all_data.get(username, {
        'categories': list(DEFAULT_CATEGORIES), 
        'feeds': list(DEFAULT_FEEDS),
        'fav_categories': ['Read Later', 'Best Of'],
        'favorites': []
    })
    # Ensure structure
    if 'categories' not in user_data: user_data['categories'] = list(DEFAULT_CATEGORIES)
    if 'feeds' not in user_data: user_data['feeds'] = list(DEFAULT_FEEDS)
    if 'favorites' not in user_data: user_data['favorites'] = []
    if 'fav_categories' not in user_data: user_data['fav_categories'] = ['Read Later']
    return user_data, all_data

def fetch_single_feed(feed):
    try:
        parsed = feedparser.parse(feed['url'])
        if not parsed.entries: return []
        articles = []
        for entry in parsed.entries[:12]:
            img = 'https://picsum.photos/400/225'
            if 'media_thumbnail' in entry: img = entry.media_thumbnail[0]['url']
            elif 'media_content' in entry:
                for m in entry.media_content:
                    if 'image' in m.get('medium', '') or 'image' in m.get('type', ''):
                        img = m['url']
                        break
            if img == 'https://picsum.photos/400/225':
                content_html = entry.get('content', [{}])[0].get('value', '') or entry.get('summary', '')
                if content_html:
                    try:
                        soup = BeautifulSoup(content_html, 'html.parser')
                        img_tag = soup.find('img')
                        if img_tag and img_tag.get('src'): img = img_tag['src']
                    except: pass
            
            summary = entry.get('summary', '')
            if not summary and 'content' in entry: summary = entry.content[0].get('value', '')
            clean_summary = ""
            if summary:
                try:
                    soup = BeautifulSoup(summary, 'html.parser')
                    clean_summary = soup.get_text()[:150] + "..."
                except: clean_summary = "Click to read more..."

            ts = time.time()
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                ts = time.mktime(entry.published_parsed)
            
            articles.append({
                'title': entry.title,
                'link': entry.link,
                'thumbnail': img,
                'summary': clean_summary,
                'source': feed['name'],
                'published': entry.get('published', 'Recent'),
                'timestamp': ts
            })
        return articles
    except: return []

# --- Routes ---

@app.route('/')
def index():
    all_data = get_all_data()
    if not all_data:
        default_user = "Default User"
        all_data[default_user] = {'categories': list(DEFAULT_CATEGORIES), 'feeds': list(DEFAULT_FEEDS), 'favorites': [], 'fav_categories': ['Read Later']}
        save_all_data(all_data)
        session['user'] = default_user
        return redirect(url_for('index'))

    if 'user' not in session: return redirect(url_for('accounts'))
    if session['user'] not in all_data:
        session.clear()
        return redirect(url_for('accounts'))

    user_data, _ = get_user_config(session['user'])
    # Render Page 2 (Home/Index)
    return render_template('page2.html', categories=user_data['categories'])

@app.route('/accounts', methods=['GET', 'POST'])
def accounts():
    all_data = get_all_data()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create':
            username = request.form.get('username')
            if username and username not in all_data:
                all_data[username] = {'categories': list(DEFAULT_CATEGORIES), 'feeds': list(DEFAULT_FEEDS)}
                save_all_data(all_data)
                session['user'] = username
                return redirect(url_for('index'))
            else: flash("User already exists.", "error")
        elif action == 'login':
            username = request.form.get('username')
            if username in all_data:
                session['user'] = username
                return redirect(url_for('index'))
        elif action == 'delete':
            username = request.form.get('username')
            if username in all_data:
                del all_data[username]
                save_all_data(all_data)
                if session.get('user') == username: session.pop('user', None)
            return redirect(url_for('accounts'))
    # Render Page 1 (Accounts)
    return render_template('page1.html', users=list(all_data.keys()))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('accounts'))

@app.route('/category/<path:category_name>')
def show_category(category_name):
    if 'user' not in session: return redirect(url_for('accounts'))
    user_data, _ = get_user_config(session['user'])
    target_feeds = [f for f in user_data['feeds'] if f['category'] == category_name]
    articles = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(fetch_single_feed, target_feeds)
        for res in results: articles.extend(res)
    articles.sort(key=lambda x: x['timestamp'], reverse=True)
    # Render Page 3 (Articles)
    return render_template('page3.html', category=category_name, articles=articles, feed_count=len(target_feeds), fav_categories=user_data['fav_categories'])

@app.route('/favorites', methods=['GET', 'POST'])
def favorites():
    if 'user' not in session: return redirect(url_for('accounts'))
    username = session['user']
    user_data, all_data = get_user_config(username)
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add_fav_cat':
            name = request.form.get('cat_name')
            if name and name not in user_data['fav_categories']: user_data['fav_categories'].append(name)
        elif action == 'del_fav_cat':
            name = request.form.get('cat_name')
            if name in user_data['fav_categories']:
                user_data['fav_categories'].remove(name)
                user_data['favorites'] = [f for f in user_data['favorites'] if f['fav_category'] != name]
        elif action == 'delete_article':
            link = request.form.get('article_link')
            user_data['favorites'] = [f for f in user_data['favorites'] if f['link'] != link]
        all_data[username] = user_data
        save_all_data(all_data)
        return redirect(url_for('favorites'))
    # Render Page 4 (Favorites)
    return render_template('page4.html', favorites=user_data['favorites'], fav_categories=user_data['fav_categories'])

@app.route('/save_article', methods=['POST'])
def save_article():
    if 'user' not in session: return redirect(url_for('accounts'))
    username = session['user']
    user_data, all_data = get_user_config(username)
    new_fav = {
        'title': request.form.get('title'), 'link': request.form.get('link'),
        'thumbnail': request.form.get('thumbnail'), 'source': request.form.get('source'),
        'timestamp': time.time(), 'fav_category': request.form.get('fav_category')
    }
    if not any(f['link'] == new_fav['link'] for f in user_data['favorites']):
        user_data['favorites'].insert(0, new_fav)
        all_data[username] = user_data
        save_all_data(all_data)
        flash("Article Saved!", "success")
    return redirect(request.referrer)

@app.route('/manager', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session: return redirect(url_for('accounts'))
    username = session['user']
    user_data, all_data = get_user_config(username)
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add_page':
            name = request.form.get('page_name')
            if len(user_data['categories']) < LIMIT_CATEGORIES and name not in user_data['categories']: user_data['categories'].append(name)
        elif action == 'delete_page':
            name = request.form.get('page_name')
            if name in user_data['categories']: user_data['categories'].remove(name)
        elif action == 'add_feed':
            cat = request.form.get('category')
            if len([f for f in user_data['feeds'] if f['category'] == cat]) < LIMIT_FEEDS_PER_CAT:
                user_data['feeds'].append({'id': str(int(time.time())), 'name': request.form.get('name'), 'url': request.form.get('url'), 'category': cat})
        elif action == 'delete_feed':
            user_data['feeds'] = [f for f in user_data['feeds'] if f['id'] != request.form.get('feed_id')]
        elif action == 'delete_category_feeds':
            user_data['feeds'] = [f for f in user_data['feeds'] if f['category'] != request.form.get('category')]
        elif action == 'delete_all_feeds':
            user_data['feeds'] = []
        all_data[username] = user_data
        save_all_data(all_data)
        return redirect(url_for('dashboard'))
    # Render Page 5 (Manager)
    return render_template('page5.html', categories=user_data['categories'], feeds=user_data['feeds'])

@app.route('/finder', methods=['GET', 'POST'])
def finder():
    if 'user' not in session: return redirect(url_for('accounts'))
    username = session['user']
    user_data, all_data = get_user_config(username)
    found_feeds = []
    error = None
    url = ""
    if request.method == 'POST':
        if request.form.get('action') == 'save_feed':
            user_data['feeds'].append({'id': str(int(time.time())), 'name': request.form.get('feed_name'), 'url': request.form.get('feed_url'), 'category': request.form.get('category')})
            all_data[username] = user_data
            save_all_data(all_data)
            flash(f"Saved {request.form.get('feed_name')}!", "success")
        url_input = request.form.get('website_url')
        if url_input:
            url = url_input if url_input.startswith('http') else 'https://' + url_input
            try:
                response = requests.get(url, timeout=5)
                soup = BeautifulSoup(response.content, 'html.parser')
                links = soup.find_all('link', type=['application/rss+xml', 'application/atom+xml'])
                for link in links: found_feeds.append({'title': link.get('title', 'RSS Feed'), 'url': urljoin(url, link.get('href'))})
                if len(found_feeds) < FINDER_RESULT_LIMIT:
                    for a in soup.find_all('a', href=True):
                        href = a['href'].lower()
                        if 'rss' in href or 'feed' in href or '.xml' in href: found_feeds.append({'title': a.get_text().strip() or "Feed", 'url': urljoin(url, a['href'])})
                seen = set()
                unique_feeds = []
                for f in found_feeds:
                    if f['url'] not in seen: seen.add(f['url']); unique_feeds.append(f)
                found_feeds = unique_feeds[:FINDER_RESULT_LIMIT]
                if not found_feeds: error = "No RSS feeds found."
            except: error = "Could not connect."
    # Render Page 6 (Finder)
    return render_template('page6.html', found_feeds=found_feeds, search_url=url, error=error, categories=user_data['categories'])

@app.route('/help')
def help_page(): 
    # Render Page 7 (Help)
    return render_template('page7.html')

@app.route('/about')
def about(): 
    # Render Page 8 (About)
    return render_template('page8.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)