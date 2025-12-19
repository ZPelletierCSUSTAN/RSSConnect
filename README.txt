RSSConnect is a app made by Zachory Pelletier. Created using Gemini Pro 3 Pro Preview AI model using Google AI Studio.

File Mapping for RSSConnect templates folder:

    page1.html = Accounts (Login)

    page2.html = Home (Categories)

    page3.html = Articles (News Feed)

    page4.html = Favorites

    page5.html = RSS Manager

    page6.html = RSS Finder

    page7.html = Help

    page8.html = About

AI prompt to generate this RSSConnect:
    "Build a comprehensive Flask-based RSS Reader named RSSConnect.

    Core Features:

        Multi-Account System: A 'Who is reading?' screen that handles multiple users without passwords.

        Categorized Feeds: Users can manage and browse news by categories (World News, Tech, etc.) with the ability to add/delete custom categories.

        RSS Finder: A tool that scrapes a website URL using BeautifulSoup to find hidden RSS/Atom links.

        Favorites System: Allow users to create folders and save specific articles into them for later reading.

        Advanced Parsing: Use ThreadPoolExecutor for fast parallel feed fetching and BeautifulSoup to extract images from article HTML if the RSS tag is missing.

    UX & Design:

        UI: Use Bootstrap 5 with the 'Simplex' theme, defaulting to a matte dark mode (#121212) with orange (#e85d04) accents.

        Navigation: Center all navigation links. Implement full Arrow-Key and Enter keyboard navigation for browsing categories and article lists.

        Previews: Articles must show a title, source, timestamp, and a short text summary preview.

    Structure: Use a numbered template system (page1.html through page8.html) for all views."