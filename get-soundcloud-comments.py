import os

import requests

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# === Config ===
SOUNDCLOUD_CLIENT_ID = os.environ.get('SOUNDCLOUD_CLIENT_ID')
SOUNDCLOUD_CLIENT_SECRET = os.environ.get('SOUNDCLOUD_CLIENT_SECRET')
TRACK_URL = os.environ.get(
    'SOUNDCLOUD_TRACK_URL',
    'https://soundcloud.com/francestherockstar/touch-my-body-x-oui-rockstar-edit-free-download',
)

AUTH_TOKEN_URL = 'https://api.soundcloud.com/oauth2/token'

if not SOUNDCLOUD_CLIENT_ID or not SOUNDCLOUD_CLIENT_SECRET:
    raise SystemExit(
        'Missing SoundCloud credentials. Set SOUNDCLOUD_CLIENT_ID and '
        'SOUNDCLOUD_CLIENT_SECRET (e.g. in a .env file; see .env.example).'
    )

def get_access_token(client_id, client_secret):
    """Get OAuth access token using client credentials flow"""
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
    
    res = requests.post(AUTH_TOKEN_URL, data=data)
    if res.status_code == 200:
        return res.json()['access_token']
    else:
        raise Exception(f"Error getting access token: {res.text}")

# Get access token for API calls
try:
    ACCESS_TOKEN = get_access_token(SOUNDCLOUD_CLIENT_ID, SOUNDCLOUD_CLIENT_SECRET)
except Exception as e:
    print(f"Failed to get access token: {e}")
    exit(1)


# === Resolve Track URL to Track ID ===
def get_track_id(track_url, access_token):
    resolve_url = f'https://api.soundcloud.com/resolve?url={track_url}'
    headers = {'Authorization': f'Bearer {access_token}'}
    res = requests.get(resolve_url, headers=headers)
    if res.status_code == 200:
        return res.json()['id']
    else:
        raise Exception(f"Error resolving URL: {res.text}")

# === Fetch Comments for a Track ID ===
def get_comments(track_id, access_token):
    url = f'https://api.soundcloud.com/tracks/{track_id}/comments'
    headers = {'Authorization': f'Bearer {access_token}'}
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        return res.json()
    else:
        raise Exception(f"Error fetching comments: {res.text}")

# === Main ===
if __name__ == '__main__':
    access_token = get_access_token(SOUNDCLOUD_CLIENT_ID, SOUNDCLOUD_CLIENT_SECRET)
    track_id = get_track_id(TRACK_URL, access_token)
    comments = get_comments(track_id, access_token)

    print(f"Found {len(comments)} comments:")
    for c in comments:
        timestamp = c.get('timestamp')
        body = c.get('body')
        user = c['user']['username']
        print(f"[{timestamp} ms] {user}: {body}")

