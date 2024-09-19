import requests
import time


class QyWxApi:
    server_url = 'https://qyapi.weixin.qq.com'
    header = {'Content-Type': 'application/json'}

    def __init__(self, corp_id, corp_secret):
        self.corp_id = corp_id
        self.corp_secret = corp_secret
        self.expiry_token = {}

    def getToken(self):
        if self.expiry_token.get('access_token') and self.expiry_token.get('expires_in') > time.time():
            return self.expiry_token.get('access_token')

        url = self.server_url + f'/cgi-bin/gettoken?corpid={self.corp_id}&corpsecret={self.corp_secret}'
        resp = requests.get(url=url)
        if resp.status_code == 200:
            resp_json = resp.json()
            if resp_json.get('errcode') == 0:
                self.expiry_token = {
                    'access_token': resp_json.get('access_token'),
                    'expires_in': time.time() + resp_json.get('expires_in') - 300
                }
                return resp_json.get('access_token')
            else:
                return
        else:
            return

    def code2Session(self, code):
        access_token = self.getToken()
        url = self.server_url + f'/cgi-bin/miniprogram/jscode2session'
        params = {
            'access_token': access_token,
            'js_code': code,
            'grant_type': 'authorization_code'
        }

        resp = requests.get(url=url, params=params)
        if resp.status_code == 200:
            resp_json = resp.json()
            if resp_json.get('errcode') == 0:
                return resp_json
            else:
                return
        else:
            return
