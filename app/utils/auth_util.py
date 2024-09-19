import requests
import os
import jwt


class JwtUtil:
    def __init__(self, secret=None):
        if secret is None:
            secret = os.urandom(24)
        self.secret_key = secret

    def createToken(self, user_id, timestamp):
        """
        将user_id、 roles写入token 中
        :param user_id: 用户 user_id
        :param timestamp: 时间戳
        :return: token
        """
        jwt_token = jwt.encode({"userid": user_id, "timestamp": timestamp}, self.secret_key, algorithm='HS256')
        return jwt_token

    def loadsToken(self, jwt_token):
        try:
            serializer = jwt.decode(jwt_token, self.secret_key, algorithms=['HS256'], options={'verify_exp': False})
            return serializer
        except Exception:
            return


class Passport:
    def __init__(self, clientId, clientSecret):
        self.baseUrl = "https://passport.hillstonenet.com"
        self.clientId = clientId
        self.clientSecret = clientSecret

    def authorize_url(self, redirect_uri, state):
        url = '{0}/OAuth/Authorize?client_id={1}&redirect_uri={2}&response_type=code&scope=full_info logout_token addr&state={3}'.format(
            self.baseUrl, self.clientId, redirect_uri, state)
        return url

    def access_token(self, code, redirect_uri):
        url = "{0}/OAuth/Token".format(self.baseUrl)
        data = {"code": code, "redirect_uri": redirect_uri,
                "grant_type": "authorization_code"}
        resp = requests.post(url, data=data, auth=(self.clientId, self.clientSecret), timeout=1200)
        access_token = resp.json()['access_token']
        return access_token

    def remove_power(self, access_token):
        headers = {'Authorization': 'Bearer ' + access_token}
        url = "{0}/OAuth/Remove".format(self.baseUrl)
        resp = requests.get(url, headers=headers, verify=False)
        return resp.json()

    def get_user_info(self, access_token):
        headers = {'Authorization': 'Bearer ' + access_token}
        url = "{0}/API/Resource/UserInfo".format(self.baseUrl)
        resp = requests.get(url, headers=headers)
        return resp.json()

