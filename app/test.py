# from datetime import datetime
# from sqlalchemy import create_engine, MetaData, Table, update

# # 创建数据库连接
# engine = create_engine('mysql+pymysql://root:Hillstone400@172.18.0.12:3306/techadmin?charset=utf8mb4')
# metadata = MetaData()

# # 使用上下文管理器确保连接在使用后被关闭
# with engine.connect() as connection:
#     # 使用反射机制加载表对象
#     auxiliary_stamp_record_table = Table('auxiliary_stamp_record', metadata, autoload_with=engine)

#     # 更新用户数据
#     # 将 ID 为 1 的记录的 reason 字段更新为 'alice_new@example.com'
#     stmt = update(auxiliary_stamp_record_table).where(auxiliary_stamp_record_table.c.file_id == "77178832-8f2f-4da5-bcf4-b7ff54c20d62"
#                                                       ).values(status='1', stamp_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
#     connection.execute(stmt)


#  pip install http://10.86.248.93:90/wechatpy-master.zip
# from datetime import datetime

# data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# print(data)  # 输出类似于 '2024-08-05 12:34:56'
# print(type(data))  # 输出 <class 'str'>





# from datetime import datetime
# import json
# from elasticsearch import Elasticsearch
# from sqlalchemy import create_engine, MetaData, Table, update, select, and_
# import ssl
# ##忽视证书
# context = ssl._create_unverified_context()
# es = Elasticsearch(['https://10.86.248.93:9200'], 
#                    http_auth=("elastic", "_DMTQ6*Rhhq_l6Qz_Rcc"), 
#                    timeout=20, 
#                    scheme="https",
#                    verify_certs=False,
#                    ssl_context=context)


# def EsInsert(body):
#     es.index(index='message_gateway', doc_type='_doc', body=body)
#     return {'msg': '操作成功！'}


# resp = es.get(index='message_gateway', doc_type='_doc', id='_VNrjJEBv1Xv3JeQRbeb')
# print(resp)







"""
    需求概述: 信创Case研发处理超时邮件提醒
    需求编号: DR23062801
    需求描述(部分):
        2.每个工作日的上午9点，系统将所有提交到CE的信创产品Case 并且提交CE两周后仍未结案的Case清单，以邮件形式推送至王元，
        邮件中Case清单包含Case的以下字段：编号、主题、优先级、客户名称、产品型号、软件版本、创建人、创建时间、当前处理人、
        提交CE时间、当前处理及当前进展。注：如果当天系统中没有相关符合条件的Case，则不进行推送
        3.信创产品Case的定义：Case中的产品型号为K系列（产品型号"SG-6000-K"开头）和国产化IDPS（产品型号以"-GC"结尾）,
        信创case定义，isRDCase：True。
"""
import redis
import html
import requests
import json
from jinja2 import Template
from elasticsearch import Elasticsearch
from datetime import datetime
from email.header import Header
import smtplib
from email.mime.text import MIMEText
import requests
from email.utils import formataddr

def search():
    es = Elasticsearch(
        [
            "esc0.tac.hillstonenet.com:9080"
        ],
        http_auth=("es", "O71MIRyJico943fnH5")
    )
    index_name = 'tech_case'

    current_time = datetime.now().timestamp() * 1000
    time_delta = 24 * 14  # 2周的小时数
    body = {
        "query": {
            "bool": {
                "must": [
                    {
                        "terms": {"status": ['Inprogress_Dialog', 'Open', 'Pending', 'Prepare_Close']}
                    },
                    {
                        "term": {"isRDCase": True}
                    },
                    {
                        "script": {
                            "script": {
                                "source": """
                                        doc['createdDate'].value.getMillis() 
                                        + params["time_delta"] * 3600 * 1000 < params["current_time"]
                                    """,
                                "params": {
                                    "current_time": current_time,
                                    "time_delta": time_delta
                                }
                            }
                        }
                    }
                ]
            }
        },
        "sort": [
            {"createdDate": "desc"}
        ]
    }
    result = es.search(index=index_name, body=body, size=10000)
    return result


def get_ce_case(cases):
    res = []
    for case in cases:
        if "products" in case:
            product_version = ""
            add = False
            for product in case['products']:
                if product['name'].lower().startswith("sg-6000-k") or product['name'].lower().endswith("-gc"):
                    add = True
                    if product['name']:
                        if product['version']:
                            product_version += f"{product['name']}:{product['version']};"
                        else:
                            product_version += f"{product['name']};"
                        case.update({"product_version": product_version})
            if add:
                res.append(case)

    return res



def get_unclosed_case():

    cases = []
    
    current_time = datetime.utcnow()
    res = search()['hits']['hits']
    for item in res:
        temp = {
                "case_number": item['_source']['caseNumber'] if "caseNumber" in item['_source'] else '',
                "subject": item['_source']['subject'] if "subject" in item['_source'] else '',
                "priority": item['_source']['priority'] if "priority" in item['_source'] else '',
                "custumer": item['_source']['endCustomer'] if "endCustomer" in item['_source'] else '',
                "create_by": item['_source']['createdByName'] if "createdByName" in item['_source'] else '',
                "handler": item['_source']['lastModifiedByName'] if 'lastModifiedByName' in item['_source'] else '',
                "status": item['_source']['status'] if 'status' in item['_source'] else '',
                "bugId": item['_source']['bugId'] if 'bugId' in item['_source'] else '',
                "create_time": '', "commit_time": '', "progress": '', "products": [], "product_version": ""
            }
        if "comments" in item['_source'] and item['_source']['comments']:
            temp["progress"] = item['_source']['comments'][-1]["commentContent"]
        if "devices" in item['_source']:
            for product in item['_source']['devices']:
                if 'productName' in product:
                    device = {"name": "", "version": ""}
                    device['name'] = product['productName']
                    if 'softwareVersionName' in product:
                        device['version'] = product['softwareVersionName']
                    temp["products"].append(device)
                    
        if "createdDate" in item['_source']:
            time_ = item['_source']['createdDate']
            time_ = time_.split('.')[0]
            temp['create_time'] = time_
            time_ = datetime.strptime(time_, "%Y-%m-%dT%H:%M:%S")
            days = (current_time - time_).days
            temp['commit_time'] = str(days) + '(天)'
        
        cases.append(temp)

    ce_cases = get_ce_case(cases)
    return len(ce_cases), ce_cases


def case_email_push(target, body, bcc=None, template_id="5510"):
    data = {
        "media_type": "email",
        "target": target,
        "template_id": template_id,
        "data": body,
        "resend": True
    }

    if bcc:
        data["bcc"] = bcc

    url = 'http://10.86.249.61/support/messagegw'
    headers = {'Content-Type': 'application/json'}
    resp = requests.post(url=url, headers=headers, json=data)
    print(resp.json())
    if resp.status_code == 200:
        return resp.json()
    else:
        return


class Emails:
    def __init__(self, source):
        self.mail_host = "smtpdm.aliyun.com"
        self.mail_host_port = 25
        self.mail_enable_ssl = False
        self.mail_user_name= 'notify@tac.hillstonenet.com'
        self.mail_password = "MvE1Upi9KZwDH3WL"
        self.mail_from_name = ""




class SendEmail:
    def __init__(self, host, host_port, user, password):
            self.host = host
            self.host_port = host_port
            self.user = user
            self.password = password

    def send(self, receivers, cc, theme, mail_msg, ssl, from_name, reply_to, bcc):
            '''
            subject 主题
            receivers 接受者
            cc 抄送
            theme 主题
            mail_msg 邮件内容
            '''
            message = MIMEText(mail_msg, 'html', 'utf-8')
            message['From'] = formataddr([from_name, self.user])
            message['To'] = ";".join(receivers)
            message['cc'] = ';'.join(cc)
            message['Reply-to'] = ';'.join(reply_to)
            message['Bcc'] = ';'.join(bcc)
            message['Subject'] = Header(theme, 'utf-8')
            fullText = message.as_string()
            print(self.host, self.host_port, self.user, self.password)
            with smtplib.SMTP(self.host, self.host_port, timeout=5) as server:
                try:
                    # server.set_debuglevel(2)
                    rply=server.login(user=self.user, password=self.password, initial_response_ok=True)
                    print(rply)
                    server.sendmail(self.user, receivers + cc + bcc, fullText)
                    return {'errcode': 0, 'errormsg': ''}
                except smtplib.SMTPRecipientsRefused as e:
                    print(f"Recipient address(es) were refused by the server:{e.recipients}")
                    for recipient, (code, msg) in e.recipients.items():
                        print(f"Recipient {recipient} refused with code {code} and message: {msg}")
                    return {'errcode': -1, 'errormsg': e}
                except Exception as e:
                    print(f"An error occurred:{e}")
                    return {'errcode': -1, 'errormsg': e}


class MessageTemplateDB():

    redis_client = redis.Redis(host="r-uf6czdtupumomqw604.redis.rds.aliyuncs.com", port=6379, 
                               username="tech", password="Q62yfMW4T2wp")
    
    def getMessageTemplate(self, template_id, language):
        key = f"message:template:{template_id}"
        if language == "en_us":
            key = f"message:template:{template_id}:en:us"
        template = self.redis_client.get(name=key)
        if template:
            template = json.loads(template)
            template = eval(html.unescape(str(template)))
            content = template.get("content")

        return content
    
    def getTitle(self, template_id, language):
        key = f"message:template:{template_id}"
        if language == "en_us":
            key = f"message:template:{template_id}:en:us"
        template = self.redis_client.get(name=key)
        if template:
            template = json.loads(template)
            template = eval(html.unescape(str(template)))
            subject = template.get("subject")
        return subject
    
    def constructData(self, template_id, language, data):
        template = self.getMessageTemplate(template_id, language)
        tm = Template(template, autoescape=False)
        data = tm.render(data)
        return data

    def constructTitle(self,template_id, language, data):
        template = self.getTitle(template_id, language)
        tm = Template(template, autoescape=False)
        data = tm.render(data)
        return data
    


if __name__ == '__main__':
    now = datetime.now().strftime('%Y-%m-%d')
    result = requests.get('http://10.86.249.61/api/v1.0/calendar/day?date=' + now)
    result = json.loads(result.text)
    if result['data']['type'] > 0:
        total, data = get_unclosed_case()
        email = Emails("notify@tac.hillstonenet.com")
        mailobj = SendEmail(email.mail_host, email.mail_host_port, email.mail_user_name, email.mail_password)
        msg_data = {
            "date": datetime.now().strftime('%Y-%m-%d'),
            "unclose_case_count": total,
            "unclose_case_list": data
        }  
        template_id = "5510"
        language = "zh_cn"
        theme = MessageTemplateDB().constructTitle(template_id, language, msg_data)
        mail_msg = MessageTemplateDB().constructData(template_id, language, msg_data)
        
        mailobj.send(["hs-dic@hillstonenet.com"], [], theme, mail_msg, email.mail_enable_ssl, email.mail_from_name, [], [])

        # msg_data = {
        #     "date": datetime.now().strftime('%Y-%m-%d'),
        #     "unclose_case_count": total,
        #     "unclose_case_list": data
        # }
        # target = ["xsliu4103@Hillstonenet.com"]
        # #target = ['wangyuan@Hillstonenet.com', 'jsong@Hillstonenet.com', 'jouyang@Hillstonenet.com','fenwang@Hillstonenet.com','ljzhang@Hillstonenet.com' ]
        # bcc = 'HS-DIC@Hillstonenet.com'
        # case_email_push(target=target, body=msg_data, bcc=bcc)
