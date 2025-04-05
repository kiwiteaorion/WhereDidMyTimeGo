# Categories for time tracking
PRODUCTIVE_CATEGORIES = {
    "Learning": [
        "udemy.com",
        "w3schools.com",
        "coursera.org",
        "edx.org",
        "khanacademy.org",
        "codecademy.com",
        "freecodecamp.org",
        "pluralsight.com",
        "linkedin.com/learning",
        "skillshare.com"
    ],
    "Work": [
        "gmail.com",
        "outlook.com",
        "office.com",
        "teams.microsoft.com",
        "slack.com",
        "github.com",
        "gitlab.com",
        "bitbucket.org",
        "jira.com",
        "trello.com",
        "asana.com"
    ],
    "Development": [
        "visual studio code",
        "pycharm",
        "intellij",
        "eclipse",
        "android studio",
        "xcode",
        "sublime text",
        "atom"
    ]
}

UNPRODUCTIVE_CATEGORIES = {
    "Social Media": [
        "facebook.com",
        "instagram.com",
        "twitter.com",
        "tiktok.com",
        "reddit.com",
        "pinterest.com",
        "snapchat.com"
    ],
    "Entertainment": [
        "youtube.com",
        "netflix.com",
        "disneyplus.com",
        "hulu.com",
        "primevideo.com",
        "spotify.com",
        "twitch.tv"
    ],
    "Gaming": [
        "steam",
        "epic games",
        "origin",
        "battle.net",
        "discord"
    ]
}

def categorize_activity(window_title, process_name):
    """
    Categorize an activity based on window title and process name
    Returns: (category, subcategory, is_productive)
    """
    # Check productive categories
    for category, items in PRODUCTIVE_CATEGORIES.items():
        for item in items:
            if item.lower() in window_title.lower() or item.lower() in process_name.lower():
                return (category, item, True)
    
    # Check unproductive categories
    for category, items in UNPRODUCTIVE_CATEGORIES.items():
        for item in items:
            if item.lower() in window_title.lower() or item.lower() in process_name.lower():
                return (category, item, False)
    
    # If no match found, return as neutral
    return ("Neutral", process_name, None) 