"""One-time local Google consent helper. Never runs in GitHub Actions.

Install google-auth-oauthlib, then run:
  python authorize_drive.py --client /path/to/downloaded-oauth-client.json --output /private/path/drive-auth.json
Paste the output file contents directly into the repository Actions secret.
"""
import argparse
import json
import os
import pathlib


def main():
    from google_auth_oauthlib.flow import InstalledAppFlow
    parser = argparse.ArgumentParser()
    parser.add_argument('--client', type=pathlib.Path, required=True)
    parser.add_argument('--output', type=pathlib.Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Output already exists; choose a new private credential file')
    # Credentials must be kept outside any repository checkout.
    location = args.output.resolve().parent
    if any((p/'.git').exists() for p in [location, *location.parents]):
        raise ValueError('Save credentials outside the repository')
    flow = InstalledAppFlow.from_client_secrets_file(str(args.client),
        ['https://www.googleapis.com/auth/drive'])
    credentials = flow.run_local_server(port=0, access_type='offline', prompt='consent')
    value = json.loads(credentials.to_json())
    value['type'] = 'authorized_user'
    if not value.get('refresh_token'):
        raise ValueError('Google did not return an offline refresh token')
    descriptor = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, 'w', encoding='utf-8') as output:
        json.dump(value, output)
    print('Authorization saved. Paste the JSON into the GitHub Actions secret, then securely remove this local copy.')


if __name__ == '__main__':
    main()
