import json
import requests
import hmac
import base64
import time
import random

from hashlib import md5
from datetime import datetime


class AliyunOpenSearch:
    Endpoint = 'http://opensearch-cn-shanghai.aliyuncs.com'

    def __init__(self, access_id, access_secret):
        self.AccessKeyId = access_id
        self.AccessKeySecret = access_secret

    def generate_auth_header(self, method, uri, body):
        date = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        x_opensearch_nonce = int(time.time() * 1e6)
        content_md5 = md5(json.dumps(body).encode('utf-8')).hexdigest()

        signature_string = '\n'.join([
            method, content_md5, 'application/json', date,
            f'x-opensearch-nonce:{x_opensearch_nonce}', uri
        ])

        signature_hmac = hmac.new(self.AccessKeySecret.encode('utf-8'), signature_string.encode('utf-8'), 'sha1')
        signature = base64.b64encode(signature_hmac.digest())
        authorization = 'OPENSEARCH ' + self.AccessKeyId + ':' + signature.decode('utf-8')

        auth_header = {
            'Authorization': authorization,
            'Content-Md5': content_md5,
            'X-Opensearch-Nonce': str(x_opensearch_nonce),
            'Date': date
        }
        return auth_header

    def stream_search(self, text, conversation_id=None, app_name='Tech_AI'):
        uri = f'/v3/openapi/apps/{app_name}/actions/multi-search'
        body = {
            "question": {
                "text": text,
                "type": "TEXT",
                "session": conversation_id
            },
            "options": {
                "retrieve": {
                    "doc": {
                        "filter": "",
                        "top_n": 5,
                        "sf": "",
                        "dense_weight": "0.7",
                        "formula": "",
                        "operator": "AND"
                    },
                    "entry": {
                        "sf": ""
                    },
                    "image": {
                        "sf": "",
                        "dense_weight": "0.7"
                    },
                    "qp": {
                        "query_extend": False, "query_extend_num": 5
                    },
                    "return_hits": False
                },
                "chat": {
                    "stream": True,
                    "prompt_config": {
                        "attitude": "normal",
                        "rule": "detailed",
                        "noanswer": "sorry",
                        "language": "Chinese",
                        "role": True,
                        "role_name": "技术部AI助手",
                        "out_format": "markdown"
                    }, "csi_level": "strict",
                    "history_max": "",
                    "link": "false",
                    "model": "opensearch-qwen",
                    "model_generation": ""
                }
            }
        }

        auth_header = self.generate_auth_header('POST', uri, body)

        with requests.post(self.Endpoint + uri, json=body, headers=auth_header, stream=True) as response:
            for line in response.iter_lines(chunk_size=10000):
                if line:
                    yield f'{line.decode("utf-8")}\n\n'
                    time.sleep(round(random.uniform(0, 0.15), 2))
