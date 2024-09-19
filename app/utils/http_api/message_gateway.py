import requests
from .msg_template import Template


class MessageGateway:
    header = {'Content-Type': 'application/json'}

    def __init__(self, server_url):
        self.server_url = server_url
        self.se_eco_email = ['5900', '5902', '5904', '5906', '5907', '5910']
        self.se_internal_affairs_email = ['5678', '5682', '5684', '5685', '5686', '5522', '5521', '5520', '6350']
        self.se_non_receiver = ['ygao@Hillstonenet.com','hxlu@Hillstonenet.com',
                                'xhdu@Hillstonenet.com','yhxie@Hillstonenet.com']

    def push(self, target, template: Template, related_id=None, cc=None, reply_to=None, resend=True,
             source=""):

        se_email = self.se_eco_email + self.se_internal_affairs_email
        if template.getTemplateId() in se_email:
            if isinstance(target, list):
                target = [receiver for receiver in target if receiver not in self.se_non_receiver] 
            if isinstance(target, str):
                target = None if target in self.se_non_receiver else target
            if isinstance(cc, list):
                cc = [receiver for receiver in cc if receiver not in self.se_non_receiver] 
            if isinstance(cc, str):
                cc = None if cc in self.se_non_receiver else cc

        data = {
            "media_type": template.getMedia(),
            "target": target,
            "template_id": template.getTemplateId(),
            "data": template.getData(),
            "resend": resend,
            "source": source
        }
        if cc:
            data["cc"] = cc
        if related_id:
            data["releated_id"] = related_id
        if reply_to:
            data["reply_to"] = reply_to

        url = '{}/support/messagegw'.format(self.server_url)
        resp = requests.post(url=url, headers=self.header, json=data)
        if resp.status_code == 200:
            return resp.json()
        else:
            return

    def push_mata(self, target, media_type, template_id, data, related_id=None, cc=None, reply_to=None, resend=True):
        data = {
            "media_type": media_type,
            "target": target,
            "template_id": template_id,
            "data": data,
            "resend": resend
        }
        if cc:
            data["cc"] = cc
        if related_id:
            data["releated_id"] = related_id
        if reply_to:
            data["reply_to"] = reply_to

        url = '{}/support/messagegw'.format(self.server_url)
        resp = requests.post(url=url, headers=self.header, json=data)
        if resp.status_code == 200:
            return resp.json()
        else:
            return

