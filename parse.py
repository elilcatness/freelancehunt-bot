import os
from dotenv import load_dotenv
import json
from datetime import datetime, timedelta
from json import JSONDecodeError

import requests
from humanize import precisedelta


class FreelanceHunt:
    api_url = 'https://api.freelancehunt.com/v2'
    projects_url = '/projects?filter[only_my_skills]=1'
    threads_url = '/threads'
    messages_url = '/threads/%d'

    def __init__(self, token):
        self.headers = {
            'Authorization': 'Bearer %s' % token,
            'Content-Type': 'application/json'
        }

    def get_response_json(self, url):
        response = requests.get(url, headers=self.headers)
        if not response:
            return print(f'Failed to get {url}')
        try:
            return response.json()
        except JSONDecodeError:
            return print(f'Failed to decode a JSON received from {url}')

    def get_messages(self):
        unread_threads_count = 0
        messages_count = 0
        threads = self.get_response_json(self.api_url +
                                         self.threads_url)['data']
        for thread in threads:
            if thread["attributes"]["is_unread"]:
                unread_threads_count += 1
                messages_count += len(
                    self.get_response_json(self.api_url +
                                           self.messages_url % thread['id'])['data'])
        return unread_threads_count, messages_count

    def get_updates(self, last_id=None):
        data = self.get_response_json(self.api_url + self.projects_url)
        output = []
        for project in data['data']:
            if last_id and project['id'] <= last_id:
                break
            attrs = project['attributes']
            if (attrs.get('status', {}).get('name') != 'Прием ставок'
                    or attrs.get('is_only_for_plus')):
                continue
            current = {
                'id': project['id'],
                'url': project['links']['self']['web'],
                'Название': attrs['name'],
                'Описание': attrs['description']
            }
            if attrs.get('skills'):
                current['Умения'] = ', '.join(
                    [sk['name'] for sk in attrs['skills']]).capitalize()
            current['Бюджет'] = (' '.join([
                str(attrs['budget'][key]) for key in attrs['budget'].keys()
            ]) if attrs.get('budget') else 'Не указан')
            current['Ставок'] = attrs['bid_count']
            dt, delta = attrs['published_at'].split('+')
            dt = dt.split('T')
            published = datetime(*map(int, dt[0].split('-')),
                                 *map(int, dt[1].split(':')))
            current['Публикация'] = precisedelta(
                datetime.utcnow() + timedelta(hours=int(delta.split(':')[0])) -
                published,
                format='%0.f') + ' ago'
            output.append(current)
        return output[::-1]


def main():
    fh = FreelanceHunt(os.getenv('fh_token'))
    print(fh.get_messages())


if __name__ == '__main__':
    load_dotenv()
    main()