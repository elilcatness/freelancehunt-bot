import json
from datetime import datetime, timedelta
from json import JSONDecodeError

import requests
from humanize import precisedelta


class FreelanceHunt:
    def __init__(self, token):
        # logging.basicConfig(filename='logs.log', format='%(asctime)s %(message)s', encoding='utf-8')
        self.url = 'https://api.freelancehunt.com/v2/projects?filter[only_my_skills]=1'
        self.headers = {'Authorization': 'Bearer %s' % token,
                        'Content-Type': 'application/json'}
        self.last_id = None

    def get_updates(self):
        response = requests.get(self.url, headers=self.headers)
        if not response:
            return print('Failed to get updates')
        try:
            data = response.json()
        except JSONDecodeError:
            return print('Failed to decode a JSON')
        output = []
        for project in data['data']:
            if project['id'] == self.last_id:
                break
            attrs = project['attributes']
            if (attrs.get('status', {}).get('name') != 'Прием ставок'
                    or attrs.get('is_only_for_plus')):
                continue
            current = {'id': project['id'],
                       'url': project['links']['self']['web'],
                       'Название': attrs['name'],
                       'Описание': attrs['description']}
            if attrs.get('skills'):
                current['Умения'] = ', '.join([sk['name'] for sk in attrs['skills']]).capitalize()
            current['Бюджет'] = (' '.join([str(attrs['budget'][key]) for key in attrs['budget'].keys()])
                                 if attrs.get('budget') else 'Не указан')
            current['Ставок'] = attrs['bid_count']
            dt, delta = attrs['published_at'].split('+')
            dt = dt.split('T')
            published = datetime(*map(int, dt[0].split('-')), *map(int, dt[1].split(':')))
            current['Публикация'] = precisedelta(
                datetime.utcnow() + timedelta(hours=int(delta.split(':')[0])) - published,
                format='%0.f') + ' ago'
            output.append(current)
        if output:
            self.last_id = output[0]['id']
        return output

    def get_last_id(self):
        return self.last_id
