import json
import os
import urllib.error
import urllib.parse
import urllib.request

SETTINGS_PATH = os.path.join(os.path.dirname(__file__), '.claude', 'settings.local.json')


def load_config():
    if os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        env = data.get('env', {})
    else:
        env = {}

    return {
        'auth_token': env.get('ANTHROPIC_AUTH_TOKEN') or os.environ.get('ANTHROPIC_AUTH_TOKEN'),
        'base_url': env.get('ANTHROPIC_BASE_URL') or os.environ.get('ANTHROPIC_BASE_URL'),
        'model': env.get('ANTHROPIC_DEFAULT_SONNET_MODEL') or os.environ.get('ANTHROPIC_DEFAULT_SONNET_MODEL') or 'deepseek/deepseek-v4-flash:free',
    }


def build_url(base, path):
    base = base.rstrip('/')
    path = path.lstrip('/')
    return f"{base}/{path}"


def request_json(url, auth_token, method='GET', payload=None):
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json',
    }
    data = None
    if payload is not None:
        data = json.dumps(payload).encode('utf-8')

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=20) as resp:
        body = resp.read().decode('utf-8')
        return resp.status, json.loads(body)


def main():
    config = load_config()
    if not config['auth_token']:
        raise SystemExit('Missing ANTHROPIC_AUTH_TOKEN in .claude/settings.local.json or environment.')
    if not config['base_url']:
        raise SystemExit('Missing ANTHROPIC_BASE_URL in .claude/settings.local.json or environment.')

    print('Using base URL:', config['base_url'])
    print('Checking model list endpoint...')

    try:
        url = build_url(config['base_url'], 'v1/models')
        status, body = request_json(url, config['auth_token'])
        print('Model list request succeeded with status', status)
        print('Response keys:', list(body.keys())[:10])
    except urllib.error.HTTPError as e:
        print('HTTPError:', e.code, e.reason)
        print(e.read().decode('utf-8', errors='replace'))
        return
    except urllib.error.URLError as e:
        print('URLError:', e.reason)
        return
    except Exception as e:
        print('Unexpected error:', repr(e))
        return

    print('\nTrying a lightweight chat completion probe...')
    probe_payload = {
        'model': config['model'],
        'messages': [
            {'role': 'user', 'content': 'Hello, are you reachable?'}
        ],
        'max_tokens': 20,
    }

    try:
        url = build_url(config['base_url'], 'v1/chat/completions')
        status, body = request_json(url, config['auth_token'], method='POST', payload=probe_payload)
        print('Chat probe request succeeded with status', status)
        print('Response type:', type(body).__name__)
        if 'choices' in body:
            print('Found choices count:', len(body['choices']))
            print('First choice content:', body['choices'][0].get('message', {}).get('content'))
        else:
            print('Response body:', body)
    except urllib.error.HTTPError as e:
        print('HTTPError:', e.code, e.reason)
        print(e.read().decode('utf-8', errors='replace'))
    except urllib.error.URLError as e:
        print('URLError:', e.reason)
    except Exception as e:
        print('Unexpected error:', repr(e))


if __name__ == '__main__':
    main()
