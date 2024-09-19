import requests


class TacApi:
    header = {'Content-Type': 'application/json'}

    def __init__(self, server_url):
        self.server_url = server_url

    def getCalendar(self, date):
        params = {"date": date}
        url = '{}/api/v1.0/calendar/day?'.format(self.server_url)
        resp = requests.get(url=url, headers=self.header, params=params)
        if resp.status_code == 200:
            return resp.json()
        else:
            return

    def getCrmSN(self, sn, page=1, size=10):
        params = {"page": page, "size": size}
        url = '{}/support/lic/crm/{}'.format(self.server_url, sn)
        resp = requests.get(url=url, headers=self.header, params=params)
        if resp.status_code == 200:
            return resp.json()
