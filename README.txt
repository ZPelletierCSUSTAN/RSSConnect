RSSConnect is an app made by Zachory Pelletier. Created using Gemini 3 Pro Preview AI model using Google AI Studio.

RSSConnect is a sophisticated, dark-themed Flask web application developed by Zachory Pelletier that features a privacy-focused multi-user account system, advanced RSS feed curation, and an integrated web scraper for finding RSS feeds.

# Design Theme:
Use Bootstrap 5 'Simplex' theme but enforce a strict Matte Dark (#121212) and Orange (#E85D04) color scheme via CSS overrides. Default Dark mode enabled with a toggle for Light mode.

# File Mapping for RSSConnect

RSSConnect/
├── app.py
├── requirements.txt
├── README.md
├── data/
│   └── user_data.json  (Auto-generated)
└── templates/
    ├── base.html       (Main Layout)
    ├── index.html      (Accounts / Login)
    ├── page1.html      (Home / Categories)
    ├── page2.html      (Articles / News Feed)
    ├── page3.html      (Favorites)
    ├── page4.html      (RSS Manager)
    ├── page5.html      (RSS Finder)
    ├── page6.html      (Help)
    └── page7.html      (About)

# Default RSS Stream
The app comes pre-loaded with the following feeds for the "Default User":

**World News**
*   CNN (YouTube)
*   BBC News (YouTube)
*   NBC News (YouTube)
*   ABC News (YouTube)

**Tech**
*   MKBHD (YouTube)
*   Unbox Therapy (YouTube)
*   Android Authority (YouTube)
*   IGN Tech

**Comics**
*   DC (YouTube)
*   IGN Comics

**TV & Movies**
*   Netflix (YouTube)
*   Marvel Entertainment (YouTube)
*   Flicks And The City (YouTube)
*   Rotten Tomatoes (YouTube)
*   IGN Movies
*   IGN TV

**Video Games**
*   IGN Games
*   GameSpot (YouTube)
*   IGN Xbox / Nintendo / PC / PlayStation

**Music**
*   Pitchfork
*   The Needle Drop (YouTube)
*   Deep Cuts (YouTube)
*   Rolling Stone

**Food**
*   One Bite Pizza Reviews (YouTube)
*   Joshua Weissman (YouTube)

**Other**
*   BBC Earth (YouTube)
*   Business Insider (YouTube)
*   Insider Tech (YouTube)

# AI Prompt:

**Project:** Build a Flask (Python) web application called 'RSSConnect'.

**Design Theme:**
Use Bootstrap 5 'Simplex' theme but enforce a strict Matte Dark (#121212) and Orange (#E85D04) color scheme via CSS overrides. Enable high-contrast text for readability.

**File Structure & Functionality:**

*   **app.py:** Main logic using Flask, `feedparser` for parsing RSS XML, `requests` + `beautifulsoup4` for scraping website headers to find feeds, and `concurrent.futures` for parallel feed fetching.
*   **templates/base.html:** Base layout containing the Navbar with centered links, Orange branding, and Theme Toggle logic.
*   **templates/index.html:** Accounts Page. Features a card-grid of users. Logic to create/delete users and auto-login as "Default User" on first run.
*   **templates/page1.html:** Home Page. Displays grid of Categories (World News, Tech, etc.) with keyboard navigation support (Arrow keys + Enter).
*   **templates/page2.html:** Articles Page. Fetches and parses RSS feeds for the selected category. Displays thumbnails (extracted via soup if missing) and summaries. Includes "Save to..." dropdown for Favorites.
*   **templates/page3.html:** Favorites Page. Allows users to create custom folders (e.g., "Read Later") and manage saved articles.
*   **templates/page4.html:** RSS Manager. Dual-column layout. Left: RSS Feed list (delete individual feeds). Right: Custom Category management (add/delete). Features a "Delete ALL Feeds" emergency button.
*   **templates/page5.html:** RSS Finder. Input field to scrape any URL (e.g., wired.com) for hidden RSS meta tags. Results allow one-click addition to specific categories.
*   **templates/page6.html:** Help page with Accordion-style guides.
*   **templates/page7.html:** About page crediting Zachory Pelletier.

**Specific Logic Implemented:**
*   **Robust Data:** `user_data.json` handles corruption automatically.
*   **Image Extraction:** If an RSS feed lacks an image, the app scrapes the article summary HTML to find a fallback image.
*   **Keyboard Nav:** JavaScript listeners for Arrow Up/Down/Left/Right to navigate grids without a mouse.
*   **Feed Limits:** Max 50 categories and 30 feeds per category to ensure performance.