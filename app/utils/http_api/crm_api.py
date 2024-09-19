import requests
import hashlib
import cgi
import io
from app.config import *
from app.utils.api_util import AppException


class CrmHttpAPI:

    def __init__(self, app_id, app_secret, server_url='http://10.88.58.28:8882'):

        self.app_id = app_id
        self.app_secret = app_secret
        self.server_url = server_url
        self.headers = {'Content-Type': 'application/json'}
        self.access_token = ''
        self.auth_data = {
            "grant_type": "application",
            "appId": self.app_id,
            "appSecret": self.app_secret
        }

    def retry(*args, **kwargs):
        def warpp(func):
            def inner(self, *args, **kwargs):
                res = func(self, *args, **kwargs)
                if isinstance(res, int):
                    self.refreshToken()
                    return func(self, *args, **kwargs)
                return res
            return inner
        return warpp

    def refreshToken(self):
        for _ in range(3):
            r = requests.post("{0}/token".format(self.server_url), data=self.auth_data)
            r.encoding = "gb2312"
            if r.status_code == 200:
                r_json = r.json()
                self.headers.update({"Authorization": 'Bearer {0}'.format(r_json['access_token'])})
                break

    @retry()
    def createLead(self, **kwargs):
        row_data = {
            'companyname': kwargs.get('company_name'),
            'fullname': f'{kwargs.get("contact_name")}({kwargs.get("contact_role")})',
            'phone': kwargs.get('contact_way'),
            'requiredescribe': kwargs.get('description'),
            'province': kwargs.get('province'),
            'city': kwargs.get('city'),
            'ownerid': kwargs.get('crm_owner_id'),
            'caseusernamae': kwargs.get('create_user'),
            'accountid': kwargs.get('crm_customer_id')
        }
        url = '{0}/api/CASE/CreateLead'.format(self.server_url)
        resp = requests.post(url, json=row_data, headers=self.headers, timeout=30)
        if resp.status_code == 200:
            return resp.json()
        else:
            return resp.status_code


class CrmLicAPI:
    license_key = 'Z8wCxY9No1Cjs9OiztYi'
    host = 'http://10.88.17.60'
    headers = {'Host': 's.lic.com'}

    def __init__(self):
        pass

    def _generateToken(self, email):
        m = hashlib.md5()
        m.update(email.encode(encoding='utf8'))
        email_md5 = m.hexdigest().upper()

        str = email_md5 + self.license_key
        m = hashlib.md5()
        m.update(str.encode(encoding='utf8'))
        token = m.hexdigest().upper()
        return token

    def createLicnse(self, base_info, lic_data):
        url = self.host + '/api/case/createlic'
        data ={"from": "internal_use"}
        data['base_info'] = base_info
        data['lic_data'] = lic_data
        resp = requests.post(url, json=data, headers=self.headers)
        return resp.json()

    def downloadLinse(self, order_id, object_name):
        from app.extensions import oss_util
        url = self.host + '/api/case/download?order_id={}'.format(order_id)
        data ={"from": "internal_use"}
        resp = requests.get(url, json=data, headers=self.headers,allow_redirects=False)
        if resp.status_code == 200:        
            try:
                _, params = cgi.parse_header(resp.headers['Content-Disposition'])
                filename = params.get('filename')
                file_meta = {
                    "ContentType": resp.headers.get("Content-Type"),
                    "ContentDisposition": f"attachment; filename={filename}"
                }
                if filename:
                    file_storage = io.BytesIO(resp.content)
                    oss_util.uploadFileStream(file_storage, "tech-uploads", file_meta, object_name)
                    return filename
            except:
                raise AppException(message=f"生成许可文件失败")
        else:
            raise AppException(message=f"请求下载许可证文件失败, status_code: {resp.status_code}")
        