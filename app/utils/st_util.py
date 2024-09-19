import os
import re
import bs4
import json
import requests
import datetime
import lxml.html
from bs4 import BeautifulSoup
from app.utils.api_util import AppException
from app.enums.st_enum import enums
from app.extensions import logger
from app.config import StConfig
from app.extensions import redis_client
from app.extensions import es_util, es_aliyun_util
from app.utils.func_util import getRandomString20
from app.utils.func_util import Common
from urllib.parse import quote
from flask import jsonify
# from playwright.sync_api import sync_playwright


# class HillstoneUniversity:

#     def __init__(self) -> None:
#         self.token_ = StConfig["hillstone_university"]["token"]
#         self.username = StConfig["hillstone_university"]["username"]
#         self.password = StConfig["hillstone_university"]["password"]

#     def onRequest(self, request):
#         if 'https://api-phx-ali.yunxuetang.cn' in request.url:
#             if 'token' in request.headers:
#                 self.token_ = request.headers['token']
#                 return


#     def getToken(self):
#         with sync_playwright() as p:
#             browser = p.chromium.launch(headless=True)
#             page = browser.new_page()
#             page.goto('https://learning.hillstonenet.com.cn/login.html')
#             page.get_by_placeholder("请输入员工邮箱/账号").fill(self.username)
#             page.get_by_placeholder("请输入密码").fill(self.password)
#             page.get_by_role("checkbox").check()
#             page.get_by_role("button", name="登 录").click()
#             page.on('request', self.onRequest)
#             page.locator(".yxtbiz-nav-top-stu__my-panel > .yxt-svg-icon").click()
#             page.get_by_placeholder("搜索课程、培训、知识、讲师、帖子...").click()
#             page.get_by_text("等保", exact=True).click()
#             page.wait_for_load_state('networkidle')
#             page.close()


#     def getResponse(self, query: str):
#         headers = {
#             'token': self.token_,
#             'Origin': 'https://learning.hillstonenet.com.cn',
#             'Referer': 'https://learning.hillstonenet.com.cn/main/',
#             "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
#                         'Chrome/80.0.3987.87 Safari/537.36 SE 2.X MetaSr 1.0',
#             "Source": "501"
#         }

#         json_data = {
#             "searchKey": query,
#             "offset": 0,
#             "limit": 100,
#             "sortType": "desc"
#         }
#         url = "https://api-search-phx-ali.yunxuetang.cn/v2/contents/types/1/search"
#         response_index = requests.post(url=url, headers=headers, json=json_data)
#         return response_index


#     def search(self, query: str):
#         try:
#             response = self.getResponse(query)
#             if response.status_code == 401:
#                 self.getToken(self.username, self.password)
#                 response = self.getResponse(query)
#             results = json.loads(response.text)
#             search_counts = results['paging']['count']
#             counts = search_counts if search_counts < 100 else 100
#             all_data = {"list": [], "style": "normal", "total": counts}
#             for data in results['datas']:
#                 temp = {"author": data['contributorsName'],
#                         'content': '',
#                         'date': data['updateTime'],
#                         'id': data['id'],
#                         'internal': False,
#                         'title': data['title'],
#                         'url': 'https://learning.hillstonenet.com.cn/kng/#/doc/play?kngId=' + data['id']}
#                 all_data['list'].append(temp)
#         except Exception as error:
#             logger.info(f"山石大学接口Token失效,{error}")
#             all_data = {"list": [], "style": "normal", "total": counts}
#         finally:
#             return all_data


def aiAsk(question: str) -> dict:
    url = "http://10.86.249.61/support/aiask"
    params = {"question": question}
    resp = requests.post(json=params, url=url)
    if resp.status_code == 200:
        data = {
            "author": "智能问答",
            "content": resp.json().get("data").get("answer"),
            "date": str(datetime.datetime.now().strftime('%Y-%m-%d')),
            "id": getRandomString20(),
            "internal": False,
            "title": question,
            "url": ""
        }
        return data
    else:
        data = {
            "author": "智能问答",
            "content": "Request failed,  please try again later !",
            "date": str(datetime.datetime.now().strftime('%Y-%m-%d')),
            "id": getRandomString20(),
            "internal": False,
            "title": question,
            "url": ""
        }
        return data


def isSnExists(sn):
    abspath = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(abspath, '../../config/meiguang.txt'), 'r', encoding="utf-8") as file:
        lines = file.readlines()
        result = False
        for line in lines:
            if sn == line[:16]:
                result = True
    return result


def getCookie():
    key = "fr:cookie"
    if redis_client.exists(key):
        source = redis_client.get(key)
        if source:
            return source
    url = "http://rd.hillstonenet.com/index.php?s=/user/user/login.shtml"
    payload = {"account": StConfig["rd"]["user"], "password": StConfig["rd"]["password"]}
    head = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",

        "Origin": "http://rd.hillstonenet.com",
        "Connection": "keep-alive",
        "Host": "rd.hillstonenet.com",
        "Referer": "http://rd.hillstonenet.com/index.php?s=/user/user/login.shtml",
        "Pragma": "no-cache",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0",
        "X-Requested-With": "XMLHttpRequest"}

    res = requests.post(url, data=payload, headers=head)
    try:
        d = res.json()
    except:
        return None
    status = d["status"]
    if status is not None and status != 1:
        return None
    else:
        redis_client.set(key, d['session_id'], 60 * 60)
        return d["session_id"]


def clearp(s: str):
    if s.startswith("<p>"):
        s = s[3:]
    if s.endswith("</p>"):
        s = s[:len(s) - 4]
    return s


class Rd:

    @staticmethod
    def searchBugzilla(keyword, n=1, s=5):
        '''
        keyword:搜索关键词
        n:检索的页码, 为0时表示从1检索到第S页
        s:n==0时, 表示需要总共检索多少页
        返回list, 所有的数据, 无数据或者出错时返回None
        '''
        session = getCookie()
        if session is None:
            logger.debug('获取Cookie信息失败')
            return None
        res = []
        if n == 0:
            for i in range(s):
                r = Rd.getpage(keyword, session, i + 1)
                if r is None or r == []:
                    break
                res.extend(r)
        else:
            res = Rd.getpage(keyword, session, n)
        return res

    @staticmethod
    def getpage(keyword, sessionid, pagenum):
        url = "http://rd.hillstonenet.com/index.php?s=/home/data/search/name/bug.shtml"
        raw = f"PHPSESSID={sessionid};ly_home_forward=http%3A%2F%2Frd.hillstonenet.com%2Findex.php%3Fs%3D%2Fhome%2Fmydata%2Findex.shtml"
        cookie = {i.split("=")[0]: i.split("=")[-1] for i in raw.split(";")}
        payload = {"page": str(pagenum), "text": keyword, "ajax": "1", "matchmode": "2"}

        head = {"Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
                "Origin": "http://rd.hillstonenet.com",
                "Connection": "keep-alive",
                "Host": "rd.hillstonenet.com",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Referer": "http://rd.hillstonenet.com/index.php?s=/home/data/search/name/bug.shtml",
                "Pragma": "no-cache",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0",
                "X-Requested-With": "XMLHttpRequest"}
        reslist = []
        try:
            raw = requests.post(url, headers=head, data=payload, cookies=cookie)
            response = raw.json()
            source = response["html"]
            if source is None:
                logger.debug("获取json失败")
                return None
            bs = BeautifulSoup(source, "html.parser")
            lis = bs.find_all("li")
            for i in lis:
                d: bs4.element.Tag = i
                comment_id = d.attrs["id"]
                a = d.find("a", {"class": "layui-table-link"})
                p = d.find("p")
                url = a.attrs["href"]
                id = url.split("id=")
                reslist.append({"title": a.text,
                                "url": url, "content": clearp(str(p)), "internal": False,
                                "author": "",
                                "id": id[1]})
            return reslist
        except:
            logger.debug("解析rd信息失败")
            return None


class FR:

    @staticmethod
    def searchFR(keyword, n=1, s=5):
        '''
        keyword:搜索关键词
        n:检索的页码, 为0时表示从1检索到第S页
        s:n==0时, 表示需要总共检索多少页
        返回list: 所有的数据, 无数据或者出错时返回None
        '''
        session = getCookie()
        if session is None:
            logger.debug('获取Cookie信息失败')
            return None
        res = []
        if n == 0:
            for i in range(s):
                r = FR.getpage(keyword, session, i + 1)
                if r is None or r == []:
                    break
                res.extend(r)
        else:
            res = FR.getpage(keyword, session, n)
        return res

    @staticmethod
    def getpage(keyword, session, i):
        url = "http://rd.hillstonenet.com/index.php?s=%2Fhome%2Fdata%2Fsearch%2Fname%2Ffr.shtml"
        payload = {"page": i, "text": keyword, "matchmode": "2", "ajax": "1", "pageCount": 100}
        raw = f"PHPSESSID={session};ly_home_forward=http%3A%2F%2Frd.hillstonenet.com%2Findex.php%3Fs%3D%2Fhome%2Fmydata%2Findex.shtml"
        cookie = {i.split("=")[0]: i.split("=")[-1] for i in raw.split(";")}
        res = requests.post(url, data=payload, cookies=cookie)
        repsonse = res.json()
        html = repsonse["html"]
        bs = bs4.BeautifulSoup(html, "html.parser")
        lis = bs.find_all("li")
        reslist = []
        for i in lis:
            d: bs4.element.Tag = i
            a = d.find("a", {"class": "layui-table-link"})
            p = d.find("p")

            url = a.attrs["href"]
            id = url.split("id=")
            reslist.append({"title": a.text,
                            "url": a.attrs["href"], "content": clearp(str(p)), "internal": False,
                            "author": "",
                            "id": id[1]})
        return reslist


class dms:
    @staticmethod
    def searchDMS(keyword, n=0, s=5):
        '''
        keyword:搜索关键词
        n:检索的页码, 为0时表示从1检索到第S页
        s:n==0时, 表示需要总共检索多少页
        返回list, 所有的数据, 无数据或者出错时返回None
        '''
        page_size = 5
        redis_key = f"dms:{keyword}"
        if redis_client.exists(redis_key):
            source = json.loads(redis_client.get(redis_key))
            if n < 0:
                return source
            else:
                l = len(source)
                if n * page_size > l:
                    return []
                start = n * page_size
                end = n * page_size + s if n * page_size < l else l
                return source[start:end]
        session = getCookie()
        if session is None:
            logger.info('获取Cookie信息失败')
            return None
        res = []
        if n < 0:
            res = dms.getpage(keyword, session)
            if res is not None and len(res) > 0:
                redis_client.set(f"dms:{keyword}", json.dumps(res), 60 * 60)
        else:
            tmp = dms.getpage(keyword, session)
            redis_client.set(f"dms:{keyword}", json.dumps(res), 60 * 60)
            l = len(tmp)
            if n * page_size > l:
                return []
            start = n * page_size
            end = n * page_size + s if n * page_size < l else l
            res = tmp[start:end]
        return res

    @staticmethod
    def getpage(keyword, session):
        url = "http://rd.hillstonenet.com/index.php?s=%2Fhome%2Fdata%2Fsearch%2Fname%2Fdms.shtml"
        payload = {"text": keyword}
        cookie = {"PHPSESSID": session}

        res = requests.post(url, data=payload, cookies=cookie)
        bs = bs4.BeautifulSoup(res.text, "html.parser")
        lis = bs.find("div", {"id": "results"}).findAll("li")

        reslist = []
        for i in lis:
            d: bs4.element.Tag = i
            a = d.find("a", {"class": "layui-table-link"})
            p = d.findAll("p")
            url = a.attrs["href"]
            id = i.attrs['id']
            context = ""
            author = ""
            docName = ""
            if len(p) >= 3:
                context = clearp(str(p[2]))
            if len(p) >= 2:
                tmp = re.search(":[^/]+?/[^/]+?/([^/]+)", p[0].text)
                if tmp is not None:
                    docName = tmp.group(1)
            if len(p) >= 1:
                tmp = re.search("users\.(.+)", p[1].text)
                if tmp is not None:
                    author = tmp.group(1)
            reslist.append({"title": a.text,
                            "url": url, "content": context, "internal": False,
                            "author": author,
                            "docName": docName,
                            "id": id})
        return reslist


def esAnalyzer(text, analyzer="ik_smart"):
    try:
        body = {
            "analyzer": analyzer,
            "text": text
        }
        result = es_util.indices.analyze(body=body)['tokens']
        return {"list": result}
    except:
        return None
    

def esSearchKB(categories, statuses, keyword, start=0, size=10, analyzer="snowball",
               highlight_pre_tags="<span class=\"highlight\">", highlight_post_tags="</span>"):
    try:
        body = {
            "from": start,
            "highlight": {
                "encoder": "html",
                "fields": {
                    "post_title.post_title": {},
                    "post_content_preview": {}
                },
                "fragment_size": 25,
                "number_of_fragments": 5,
                "post_tags": [highlight_post_tags],
                "pre_tags": [highlight_pre_tags]
            },
            "min_score": 10.0,
            "query": {
                "bool": {
                    "filter": [
                        {"bool": {"minimum_should_match": 1, "should": []}},
                        {"bool": {"minimum_should_match": 1, "should": []}}
                    ],
                    "should": [{
                        "multi_match": {
                            "fields": ["post_content_preview^1", "post_title.post_title^5", "terms.post_tag.name^10"],
                            "minimum_should_match": 1,
                            "query": "",
                            "slop": 5,
                            "type": "most_fields"
                        }
                    }]
                }
            },
            "size": size,
            "sort": [{"_score": {"order": "desc"}}]
        }

        for cat in categories:
            match_phrase = {"match_phrase": {"terms.category.name": {"query": cat}}}
            body["query"]["bool"]["filter"][0]["bool"]["should"].append(match_phrase)

        for s in statuses:
            match_phrase = {"match_phrase": {"post_status": {"query": s}}}
            body["query"]["bool"]["filter"][1]["bool"]["should"].append(match_phrase)

        body["query"]["bool"]["should"][0]["multi_match"]["query"] = keyword

        return es_aliyun_util.search(index='kbhillstonenetcom*', doc_type='post', body=body)
    except Exception as error:
        logger.info(error)
        return None


def esSearchCase(keyword, start=0, size=10, analyzer="snowball", highlight_pre_tags="<span class=\"highlight\">",
                 highlight_post_tags="</span>"):
    try:
        body = {
            "from": start,
            "highlight": {
                "encoder": "html",
                "fields": {
                    "subject": {},
                    "description": {},
                    "solution": {}
                },
                "fragment_size": 25,
                "number_of_fragments": 5,
                "post_tags": [highlight_post_tags],
                "pre_tags": [highlight_pre_tags]
            },
            "query": {
                "bool": {
                    "minimum_should_match": 1,
                    "should": [
                        {"term": {"bugId": keyword}},
                        {"term": {"caseNumber": keyword}},
                        {"term": {"caseNumber_Abb": keyword}},
                        {"nested": {"path": "contacts", "query": {"term": {"contacts.info": keyword}}}},
                        {"nested": {"path": "contacts", "query": {"term": {"contacts.info_Abb": keyword}}}},
                        {"term": {"description": keyword}},
                        {"nested": {"path": "devices", "query": {"term": {"devices.sN": keyword}}}},
                        {"nested": {"path": "events", "query": {"term": {"events.externalTarget": keyword}}}},
                        {"nested": {"path": "events", "query": {"term": {"events.externalTarget_Abb": keyword}}}},
                        {"nested": {"path": "tags", "query": {"term": {"tags.lable": keyword}}}},
                        {"nested": {"path": "comments", "query": {"multi_match": {"analyzer": analyzer, "fields":
                            ["comments.commentContent"], "query": keyword, "slop": 5, "type": "phrase"}}}},
                        {"multi_match": {"analyzer": analyzer, "fields":
                            ["subject^10", "endCustomer^10", "accountName^10", "solveProgress^3", "logInfo",
                             "description", "solution"], "query": keyword, "slop": 5, "type": "phrase"}}
                    ]
                }
            },
            "size": size,
            "sort": [{"_score": {"order": "desc"}}],
            "_source": {
                "includes": ["caseNumber", "subject", "createdDate", "status", "description", "solution",
                             "currentQueueStatus", "handlerId", "handlerName", "accountName", "priority",
                             "lastModifiedDate", "firstResponsibleRersonName"]
            }
        }
        return es_util.search(index='tech_case*', body=body)
    except Exception as error:
        logger.info(error)
        return None


def esSearchS(statuses, keyword, start=0, size=10, analyzer="snowball", highlight_pre_tags="<span class=\"highlight\">",
              highlight_post_tags="</span>"):
    try:
        body = {
            "from": start,
            "highlight": {
                "encoder": "html",
                "fields": {
                    "post_title.post_title": {},
                    "post_content_preview": {}
                },
                "fragment_size": 25,
                "number_of_fragments": 5,
                "post_tags": [highlight_post_tags],
                "pre_tags": [highlight_pre_tags]
            },
            "query": {
                "bool": {
                    "filter": [],
                    "should": [{
                        "multi_match": {
                            "analyzer": analyzer,
                            "fields": ["post_content_preview^1", "post_title.post_title^5", "terms.post_tag.name^10"],
                            "minimum_should_match": 1,
                            "query": keyword,
                            "slop": 5,
                            "type": "most_fields"
                        }
                    }]
                }
            },
            "size": size,
            "sort": [{"_score": {"order": "desc"}}]
        }
        for s in statuses:
            match_phrase = {"match_phrase": {"post_status": s}}
            body["query"]["bool"]["filter"].append(match_phrase)
        return es_util.search(index='shillstonenetcomcn-post-1', doc_type='post', body=body)
    except Exception as error:
        logger.info(error)
        return None


def searchAssistantView(size, page):
    body = {
        "query": {"bool": {"must": [{"match_all": {}}]}},
        "sort": [{"solve": {"order": "asc"}}, {"last_reply_time": {"order": "desc"}}],
    }
    res = es_util.search(index='tac_wework_assistant_view', doc_type='_doc', body=body)
    total = res['hits']['total']

    body = {
        "query": {"bool": {"must": [{"match_all": {}}]}},
        "sort": [{"solve": {"order": "asc"}}, {"last_reply_time": {"order": "desc"}}],
        "size": size,
        "from": size * (page - 1)
    }
    session_list = []
    res = es_util.search(index='tac_wework_assistant_view', doc_type='_doc', body=body)
    for hit in res['hits']['hits']:
        _source = hit['_source']
        last_servicer = ''
        if not _source.get('request_userid'):
            continue

        body = {
            "query": {
                "bool":{
                    "must":[{"match_all":{}},{"match_phrase":{"room_id":{"query":_source['room_id']}}}],
                    "must_not": [{"match_phrase": {"sender_userid": {"query": _source['request_userid']}}}]
                }
            },
            "sort": [{"send_time": {"order": "desc"}}],
            "size": 1,
        }
        res = es_util.search(index='tac_wework_assistant_message*', doc_type='_doc', body=body)
        message = res['hits']['hits']
        if message:
            last_servicer = message[0].get('_source').get('sender_userid') if message[0].get('_source') else ''
        last_reply_time = datetime.datetime.fromtimestamp(_source['last_reply_time']/1000).strftime('%Y-%m-%d %H:%M:%S')
        solve = _source['solve'] if 'solve' in _source.keys() else False
        data = {
            "user_name": "{}@{}".format(_source['request_name'], _source['position']),
            "reply_time": last_reply_time,
            "content": _source['content'],
            "last_servicer": last_servicer,
            "servicer": _source['servicer_userid'],
            "room_url": 'https://support.tac.hillstonenet.com.cn/service/wework/chat/room?room={}'.format(_source['room_id']),
            "solve": solve,
        }
        session_list.append(data)
    return session_list, total


class Hsdoc:

    @staticmethod
    def search(keyword, n=0, s=10):
        cookies_dict = Hsdoc.getCookie()
        if cookies_dict is not None:
            headers = {"Accept": "application/json, text/plain, */*"}
            url = '{0}/hohs/index/searchDocKeyword?keyword={1}&productName=&docType=&pageIndex={2}&pageSize={3}'.format(
                StConfig['idocs']['baseurl'], keyword, n+1, s)
            try:
                resp = requests.get(url, headers=headers, cookies=cookies_dict, verify=True)
                result = resp.json()
                return result
            except:
                cookies_dict = Hsdoc.getCookie(True)
                resp = requests.get(url, headers=headers, cookies=cookies_dict, verify=True, timeout=3)
                result = resp.json()
                return result
        else:
            logger.info('获取Cookie信息失败')
            return None

    @staticmethod
    def getCookie(force=False):
        redis_key = "idocs:{0}:cookies".format(StConfig['idocs']['username'])
        if redis_client.exists(redis_key) and force is False:
            return json.loads(redis_client.get(redis_key))
        else:
            cookies_dict = Hsdoc.getPassportCookie()
            if cookies_dict is None: return None
            params = {
                "client_id": "815183ae5da34fef86ebbf9ff1f7bff2",
                "redirect_uri": "{0}/hohs/#/loginpage".format(StConfig['idocs']['baseurl']),
                "response_type": "code",
                "scope": "full_info",
                "state": "faielkjf3235325klj4lk23j4lk2j",
            }
            url = 'https://passport.hillstonenet.com/OAuth/Authorize'
            resp = requests.get(url, params=params, cookies=cookies_dict, allow_redirects=True, timeout=3)
            if resp.status_code == 404 and 'Set-Cookie' in resp.headers:
                cookies_dict = requests.utils.dict_from_cookiejar(resp.cookies)
                url = '{0}/hohs/login'.format(StConfig['idocs']['baseurl'])
                data = {'username': StConfig['idocs']['username'],
                    'password': '', 'remember-me': 'true'}
                resp = requests.post(url, data=data, cookies=cookies_dict, allow_redirects=True)
                if resp.status_code == 200:
                    cookies_dict = requests.utils.dict_from_cookiejar(resp.cookies)
                    redis_client.set(redis_key, json.dumps(cookies_dict), 24*60*60)
                    return cookies_dict
            else:
                error_msg = ""
                for index, resp in enumerate(resp.history):
                    error_msg = error_msg+"{0}:{1}=>{2}\n".format(index, resp.url, resp.status_code)
                logger.info('登录idocs失败:{0}'.format(error_msg))
            return None

    @staticmethod
    def getPassportCookie():
        redis_key = "passport:{0}:cookies".format(
            StConfig['idocs']['username'])
        if redis_client.exists(redis_key):
            return json.loads(redis_client.get(redis_key))
        else:
            url = 'https://passport.hillstonenet.com/Account/Login?ReturnUrl=%2F'
            resp = requests.get(url)
            if resp.status_code != 200:
                logger.info('获取passport登录页失败:http status code:{}'.format(resp.status_code))
                return None
            cookies_dict = requests.utils.dict_from_cookiejar(resp.cookies)
            html = lxml.html.fromstring(resp.text.encode('utf-8'))
            RequestVerificationToken = html.xpath("//input[@name='__RequestVerificationToken']/@value")
            data = {
                'UserName': StConfig['idocs']['username'],
                'Password': StConfig['idocs']['password'],
                'RememberMe': 'true',
                '__RequestVerificationToken': RequestVerificationToken
            }
            resp = requests.post(url, data=data, cookies=cookies_dict, verify=True, allow_redirects=False)
            if 'Location' in resp.headers and resp.headers['Location'] == '/':
                cookies_dict = requests.utils.dict_from_cookiejar(
                    resp.cookies)
                redis_client.set(redis_key, json.dumps(cookies_dict), 7*24*60*60)
                return cookies_dict
            else:
                logger.info('HTTP头部不存在Location,Header:{0}'.format(resp.headers))
                return None


def getOverViewContent(q: str, role_department: str ):
    source = [
        {"key": "kb", "name": "知识库"},
        {"key": "case", "name": "个案"},
        {"key": "s", "name": "S站点"}
        # {"key": "idocs", "name": "技术文档系统"},
        # {"key": "bugzilla", "name": "Bugzilla"},
        # {"key": "dms", "name": "DMS"},
        # {"key": "fr", "name": "FR"},
        # {"key": "aiask", "name": '智能问答'}
        # {"key": "hillstone_university", "name": '山石大学'}
    ]
    # try:
    #     url = "http://10.86.249.61:8081/support/device/{}"
    #     if requests.get(url.format(q)).json().get("code") == 0 or isSnExists(q):
    #         source.append({"key": "device_info", "name": "设备信息"})
    # except:
    #     pass
    if role_department == "other":
        source = [
            {"key": "kb", "name": "知识库"}
            # {"key": "idocs", "name": "技术文档系统"},
        ]
    return source


def overview(q: str, next_id : int, role_department: str):
    source = getOverViewContent(q, role_department)
    if next_id > len(source): raise AppException("Search failed, out of source range!")
    data = {"source": [], "next": {}}
    if next_id == 0:
        kb_result = esSearchKB(list(enums["kb_categories"].values()), list(enums["kb_statuses"].values()), q, 0, 0, "ik_max_word")
        kb_count = kb_result["hits"]["total"] if kb_result else 0
        data["source"].append({"key": "kb", "name": "知识库", "total": kb_count})
        case_result = esSearchCase(q, 0, 0, "ik_max_word")
        case_count = case_result["hits"]["total"] if case_result else 0
        data["source"].append({"key": "case", "name": "个案", "total": case_count})
        # for s in source:
        #     if s.get("key")=="device_info":
        #         data["source"].append({"key": "device_info", "name": "设备信息", "total": 1})
        # try:
        #     idocs_result = Hsdoc.search(q, 0, 10)
        # except Exception:
        #     idocs_result = None
        # idocs_count = idocs_result["total"] if idocs_result else 0
        # data["source"].append({"key": "idocs", "name": "技术文档系统", "total": idocs_count})
        s_result = esSearchS(["publish"], q, 0, 0, "ik_max_word")
        s_count = s_result["hits"]["total"] if s_result else 0
        data["source"].append({"key": "s", "name": "S站点", "total": s_count})
        # data["next"] = {"id": 4, "name": "Bugzilla", "total": len(source)}
    else:
        next_source = source[next_id]
        next_id = next_id + 1
        next_name = source[next_id]["name"] if next_id < len(source) else ""
        data["next"] = {"id": next_id, "name": next_name, "total": len(source)}
        if next_id == len(source):
            next_id = next_id - 1
            data["next"] = {"id": -1, "name": "", "total": len(source)}
        if next_source["key"] == "case":
            case_result = esSearchCase(q, 0, 10, "ik_max_word")
            case_count = case_result["hits"]["total"] if case_result else 0
            data["source"].append({"key": "case", "name": "个案", "total": case_count})
        elif next_source["key"] == "idocs":
            idocs_result = Hsdoc.search(q, 0, 10)
            idocs_count = idocs_result["total"] if idocs_result else 0
            data["source"].append({"key": "idocs", "name": "技术文档系统", "total": idocs_count})
        elif next_source["key"] == "bugzilla":
            Bugzilla_result = Rd.searchBugzilla(q, 0, 5)
            Bugzilla_count = len(Bugzilla_result) if Bugzilla_result else 0
            data["source"].append({"key": "bugzilla", "name": "Bugzilla", "total": Bugzilla_count})
        elif next_source["key"] == "dms":
            dms_result = dms.searchDMS(q, -1, 0)
            dms_count = len(dms_result) if dms_result else 0
            data["source"].append({"key": "dms", "name": "DMS", "total": dms_count})
        elif next_source["key"] == "fr":
            fr_result = FR.searchFR(q, 0, 5)
            fr_count = len(fr_result) if fr_result else 0
            data["source"].append({"key": "fr", "name": "FR", "total": fr_count})
        elif next_source["key"] == "aiask":
            data["source"].append({"key": "Jarvis", "name": "智能问答","total": 1})
        # elif next_source["key"] == "hillstone_university":
        #     total = HillstoneUniversity().search(query=q).get("total")
        #     data["source"].append({"key": "hillstone_university", "name": "山石大学", "total": total})
        # elif next_source["key"] == "device_info":
        #     data["source"].append({"key": "device_info", "name": "设备信息", "total": 1})
        else:
            raise AppException("Search failed, out of source range!")
    return data



def getStSearchDetail(q: str, t: str, s: int, n: int, role_department: str, user_id: str):
    data = None
    if t == 'kb':
        try:
            kb_result = esSearchKB(list(enums["kb_categories"].values()), list(enums["kb_statuses"].values()), q, n * s, s, "ik_max_word")
            data = {'total': kb_result["hits"]["total"], 'style': 'normal', 'list': []}
            for hit in kb_result['hits']['hits']:
                id = hit['_id']
                title = hit['_source']['post_title']
                if 'highlight' in hit and "post_title.post_title" in hit['highlight']:
                    title = '...'.join(hit['highlight']['post_title.post_title'])
                content = hit['_source']['post_content_preview']
                if 'highlight' in hit and "post_content_preview" in hit['highlight']:
                    content = '...'.join(hit['highlight']['post_content_preview'])
                url = hit['_source']['permalink']
                author = hit['_source']['post_author']['display_name']
                date = Common.utc2Local(hit['_source']['post_modified_gmt']).strftime('%Y-%m-%d') if 'post_modified_gmt' in \
                                                                                                    hit['_source'] else ''
                post_internal = False
                if 'viewscope' in hit['_source']['terms']:
                    for c in hit['_source']['terms']['viewscope']:
                        if 'hillstoneinternal' in c['slug'] or 'tacinternal' in c['slug']:
                            post_internal = True
                d = {'id': id, 'title': title, 'content': content, 'internal': post_internal,
                    'url': url, 'author': author, 'date': date}
                data['list'].append(d)
        except Exception as error:
            logger.info(error)
            data = {"list":[], "style": "normal", "total": 0}

    elif t == 's':
        try:
            s_result = esSearchS(['publish'], q, n * s, s, "ik_max_word")
            data = {'total': s_result["hits"]["total"], 'style': 'normal', 'list': []}
            for hit in s_result['hits']['hits']:
                id = hit['_id']
                title = hit['_source']['post_title']
                if 'highlight' in hit and "post_title.post_title" in hit['highlight']:
                    title = '...'.join(hit['highlight']['post_title.post_title'])
                content = hit['_source']['post_content_preview']
                if 'highlight' in hit and "post_content_preview" in hit['highlight']:
                    content = '...'.join(hit['highlight']['post_content_preview'])
                url = hit['_source']['permalink']
                author = hit['_source']['post_author']['display_name']
                date = Common.utc2Local(hit['_source']['post_modified_gmt']).strftime('%Y-%m-%d') if 'post_modified_gmt' in \
                                                                                                    hit['_source'] else ''
                post_internal = False
                for c in hit['_source']['terms']['category']:
                    if 'internal' in c['slug']:
                        post_internal = True
                d = {'id': id, 'title': title, 'content': content, 'internal': post_internal,
                    'url': url, 'author': author, 'date': date}
                data['list'].append(d)
        except Exception as error:
            logger.info(error)
            data = {"list":[], "style": "normal", "total": 0}


    elif t == 'case':
        try:
            case_result = esSearchCase(q, n * s, s, "ik_max_word")
            data = {'total': case_result["hits"]["total"], 'style': 'normal', 'list': []}
            for hit in case_result['hits']['hits']:
                id = hit['_id']
                title = '[{0}]{1}'.format(hit['_source']['caseNumber'], hit['_source']['subject'])
                if 'highlight' in hit and "subject" in hit['highlight']:
                    title = '[{0}]'.format(hit['_source']['caseNumber']) + '...'.join(hit['highlight']['subject'])
                content = ''
                if 'highlight' in hit and "description" in hit['highlight']:
                    content = content + '...'.join(hit['highlight']['description'])
                if 'highlight' in hit and "solution" in hit['highlight']:
                    content = content + '...'.join(hit['highlight']['solution'])
                if len(content) == 0:
                    content = hit['_source']['description']
                if role_department == "技术支持中心":
                    url = 'https://support.tac.hillstonenet.com.cn/Case/Detail/{0}?k={1}&rf=UnionSearch'.format(
                        hit['_source']['caseNumber'], quote(q))
                else:
                    url = 'https://support.hillstonenet.com.cn/Case/Detail/{0}?k={1}&rf=UnionSearch'.format(
                        hit['_source']['caseNumber'], quote(q))
                author = hit['_source']['handlerName']
                if 'currentQueueStatus' in hit['_source'] and 'handlerId' in hit['_source'] and hit['_source'][
                    'currentQueueStatus'] == 'InQueue' and hit['_source']['handlerId'] != user_id:
                    title = '[{0}]*******'.format(hit['_source']['caseNumber'])
                    content = '******'
                    author = '******'
                date = Common.utc2Local(hit['_source']['createdDate']).strftime('%Y-%m-%d') if 'createdDate' in hit[
                    '_source'] else ''
                d = {'id': id, 'title': title, 'content': content, 'internal': False,'url': url, 'author': author, 'date': date}
                data['list'].append(d)
        except Exception as error:
            logger.info(error)
            data = {"list":[], "style": "normal", "total": 0}

    elif t == 'idocs':
        try:
            idocs_result = Hsdoc.search(q, n, s)
            data = {'total': idocs_result["total"], 'style': 'normal', 'list': []}
            if idocs_result["total"] > 0:
                for item in idocs_result["data"]:
                    url = '{0}/#/detail?keyword={1}&path={2}&doc={3}'.format(
                        StConfig['idocs']['baseurl'], q, quote(item["path"], safe=''), item["docName"])
                    d = {'id': None, 'title': item["productName"] + '-' + item["chapName"], 'content': item["content"],
                            'internal': False, 'url': url, 'author': 'TechDocs', 'docName': item["docName"]}
                    data['list'].append(d)
        except Exception as error:
            logger.info(error)
            data = {"list":[], "style": "normal", "total": 0}

    elif t == 'bugzilla':
        try:
            data = {"total": 0, "style": "normal", "list": []}
            BugZilla_result = Rd.searchBugzilla(q, (n + 1) // 2 + 1, s) if (n + 1) % 2 != 0 else Rd.searchBugzilla(
                q, (n + 1) // 2, s)
            if BugZilla_result is not None:
                data["total"] = min(5, len(BugZilla_result))
                data['list'].extend(BugZilla_result[:5])

        except Exception as error:
            logger.info(error)
            data = {"list":[], "style": "normal", "total": 0}

    elif t == 'fr':
        try:
            data = {"total": 0, "style": "normal", "list": []}
            fr_result = FR.searchFR(q, (n + 1) // 2 + 1, s) if (n + 1) % 2 != 0 else FR.searchFR(q,(n + 1) // 2,s)
            if fr_result is not None:
                data["total"] = min(5, len(fr_result))
                data['list'].extend(fr_result[:5])
        except Exception as error:
            logger.info(error)
            data = {"list":[], "style": "normal", "total": 0}

    elif t == "dms":
        try:
            dms_result = dms.searchDMS(q, n, s)
            if dms_result is not None:
                data = {"total": len(dms_result), "style": "normal", "list": dms_result}
            else:
                data = {"total": 0, "style": "normal", "list": []}
        except Exception as error:
            logger.info(error)
            data = {"list":[], "style": "normal", "total": 0}

    # elif t == "hillstone_university":
    #     try:
    #         data = HillstoneUniversity().search(q)
    #         data["list"] = data["list"][n * 5: n * 5 + 5]
    #     except Exception as error:
    #         logger.info(error)
    #         data = {"list":[], "style": "normal", "total": 0}

    elif t == "Jarvis":
        try:
            data = {"total": 1, "style": "normal", "list": [aiAsk(question=q)]}
        except Exception as error:
            logger.info(error)
            data = {"total": 0, "style": "normal", "list": []}

    elif t == "device_info":
        try:
            url = "http://10.86.249.61:8081/support/device/{}"
            result = requests.get(url.format(q)).json()["data"]
            sn = result.get("sn")
            data = {"style": "normal", "total": 1, "list": [{"sn": sn, "product_name": result.get("product_name"),
                                                             "service_deadline": result.get("warranty_date"),
                                                             "customer": result.get("customer"),
                                                             "meiguang": isSnExists(q), "data_time": "2023-06-16"}]}
        except Exception as error:
            logger.info(error)
            data = {"list":[], "style": "normal", "total": 0}
    else:
        pass

    return jsonify({'code': 0, 'data': data, 'message': ''})

