import copy

from app.extensions import es_util, es_aliyun_util
from elasticsearch import exceptions
from app.utils.func_util import datetimeReducedEightHour


class ESService:

    @staticmethod
    def queryCrmSysUserByEmail(internalemail):
        index_name = "crm_sys_user"
        query = {
            "bool": {
                "must": [{"term": {"internalemail": internalemail}}],
                "filter": [{
                    "bool": {"must_not": {"bool": {"should": [{"match": {"Hide": '停用'}}], "minimum_should_match": 1}}}
                }]
            }
        }

        body = {"query": query, "size": 1, "from": 0}
        res = es_util.search(index=index_name, doc_type='doc', body=body)
        if res['hits']['total'] > 0:
            return res['hits']['hits'][0]['_source']
        return

    @staticmethod
    def queryCrmAccountByAccountName(account_name: str, size=10, page=1) -> (int, list):
        index_name = "crm_account"
        query = {
            "bool": {
                # "must": [
                #     {"script": {"script": {"lang": "painless", "source": "doc['_id'].values[0].length() == 36"}}}
                # ],
                "must": [{"query_string": {"query": account_name}}],
                "should": [
                    {"match_phrase": {"Alias": {"query": account_name, "slop": 1, "boost":100}}},
                    {"match": {"AccountName": {"query": account_name}}},
                    {"match_phrase": {"AccountName": {"query": account_name, "slop": 5}}}
                ],
                "minimum_should_match": 1,
                "filter": [
                    {
                        "bool": {"must_not": {"bool": {
                            "should": [{"match": {"Hide": True}}, {"match": {"Status": "停用"}}],
                            "minimum_should_match": 1
                        }}}
                    }
                ]
            }
        }

        body = {"query": query, "size": size, "from": size * (page - 1)}
        res = es_util.search(index=index_name, doc_type='_doc', body=body)

        data = []
        total = res['hits']['total']
        for account in res['hits']['hits']:
            data.append(account['_source'])

        return total, data

    @staticmethod
    def queryCrmAccountByAccountId(account_id):
        index_name = "crm_account"
        query = {"match_phrase": {"AccountId": account_id}}

        body = {"query": query}
        res = es_util.search(index=index_name, doc_type='_doc', body=body)

        if res['hits']['total'] > 0:
            return res['hits']['hits'][0]['_source']

        return

    @staticmethod
    def queryCrmSysUserByUserName(username, size=10, page=1) -> (int, list):
        index_name = "crm_sys_user"
        query = {
            "bool": {
                "must": [{"query_string": {"query": username}}],
                "should": [
                    {"match": {"username": {"query": username}}},
                    {"match_phrase": {"username": {"query": username, "slop": 2}}}
                ],
                "minimum_should_match": 1,
                "must_not": [{"match": {"Status": "停用"}}],
            }
        }

        body = {"query": query, "size": size, "from": size * (page - 1)}
        res = es_util.search(index=index_name, doc_type='doc', body=body)

        data = []
        total = res['hits']['total']
        for account in res['hits']['hits']:
            data.append(account['_source'])

        return total, data

    @staticmethod
    def queryCrmSystemUserByUserId(userid):
        index_name = "crm_sys_user"
        query = {"match_phrase": {"userid": userid}}

        body = {"query": query}
        res = es_util.search(index=index_name, doc_type='doc', body=body)

        if res['hits']['total'] > 0:
            return res['hits']['hits'][0]['_source']

        return

    @staticmethod
    def querySeWorkByProjectId(project_id):
        index_name = "se_work"
        query = {
            "match": {
                "_id": project_id
            }
        }

        body = {"query": query}
        res = es_aliyun_util.search(index=index_name, doc_type='_doc', body=body)
        if res['hits']['total'] > 0:
            return res['hits']['hits'][0]['_source']

        return

    @staticmethod
    def querySeWorkByFilter(user_ids, **parmas) -> (int, list):
        index_name = "se_work"

        query = {"bool": {}}
        user_match = {"bool": {"should": []}}
        if user_ids:
            if user_ids[0] == "*":
                user_match["bool"]["should"].append({"wildcard": {"created_by_id": user_ids[0]}})
            else:
                if not (parmas.get("owner_id") and parmas.get("created_by_id")) and not parmas.get("participants"):
                    user_match["bool"]["should"].append({"terms": {"participant_ids": user_ids}})
                user_match["bool"]["should"].append({"terms": {"created_by_id": user_ids}})
                user_match["bool"]["should"].append({"terms": {"owner_id": user_ids}})
        query["bool"]["must"] = [user_match]

        if parmas.get("participants"):
            participant = {"bool": {"should": []}}
            participant["bool"]["should"].append({"terms": {"participant_ids": parmas.get("participants")}})

            if query["bool"].get("must"):
                query["bool"]["must"].append(participant)
            else:
                query["bool"]["must"] = [participant]

        if parmas.get("created_by_id"):
            create_by_user = {"bool": {"should": []}}
            create_by_user["bool"]["should"].append({"terms": {"created_by_id": parmas.get("created_by_id")}})

            if query["bool"].get("must"):
                query["bool"]["must"].append(create_by_user)
            else:
                query["bool"]["must"] = [create_by_user]

        if parmas.get("owner_id"):
            owner_user = {"bool": {"should": []}}
            owner_user["bool"]["should"].append({"terms": {"owner_id": parmas.get("owner_id")}})

            if query["bool"].get("must"):
                query["bool"]["must"].append(owner_user)
            else:
                query["bool"]["must"] = [owner_user]

        if parmas.get("query"):
            project_fields = ["subject", "account_name", "contact_info", "contact_name", "project_number"]
            project_match = [{"match_phrase": {field: {"query": parmas.get("query"), "slop": 2}}} for field in
                             project_fields]

            task_fields = ["tasks.subject", "tasks.account_name", "tasks.contact_info", "tasks.contact_name",
                           "tasks.task_number"]
            task_match = {
                "nested": {
                    "path": "tasks",
                    "query": {
                        "bool": {
                            "should": [{"match_phrase": {field: {"query": parmas.get("query"), "slop": 2}}} for field in
                                       task_fields]
                        }
                    }
                }
            }

            record_fields = ["tasks.record.record_content.content"]
            record_match = {
                "nested": {
                    "path": "tasks",
                    "query": {
                        "nested": {
                            "path": "tasks.record",
                            "query": {
                                "bool": {
                                    "should": [{"match_phrase": {field: {"query": parmas.get("query"), "slop": 2}}} for
                                               field in record_fields]
                                }
                            }
                        }
                    }
                }
            }

            query_match = {"bool": {"should": [project_match, task_match, record_match]}}
            if query["bool"].get("must"):
                query["bool"]["must"].append(query_match)
            else:
                query["bool"]["must"] = [query_match]

        if parmas.get("date_range"):
            query["bool"]["filter"] = [{
                "range": {
                    "created_date": {
                        "gte": parmas.get("date_range")[0],
                        "lte": parmas.get("date_range")[1],
                        "format": "yyyy-MM-dd HH:mm:ss"
                    }
                }
            }]

        if parmas.get("update_date_range"):
            query["bool"]["filter"] = [{
                "range": {
                    "last_modified_date": {
                        "gte": parmas.get("update_date_range")[0],
                        "lte": parmas.get("update_date_range")[1],
                        "format": "yyyy-MM-dd HH:mm:ss"
                    }
                }
            }]

        sort = [{"created_date": {"order": "desc"}}]
        if parmas.get("order_column") and parmas.get("order_direct"):
            sort = [{parmas.get("order_column"): {"order": parmas.get("order_direct")}}]

        if parmas.get("status"):
            status_match = {"bool": {"should": []}}
            for status in parmas.get("status"):
                status_match["bool"]["should"].append({"match": {"status": status}})

            if query["bool"].get("must"):
                query["bool"]["must"].append(status_match)
            else:
                query["bool"]["must"] = [status_match]

        if 'filter' in query["bool"].keys() and len(query["bool"].keys()) == 1:
            query["bool"] = {"must": [{"match_all": {}}]}

        size = parmas.get("size") if parmas.get("size") else 1000
        page = parmas.get("page") if parmas.get("page") else 1
        body = {"query": query, "size": size, "from": size * (page - 1), "sort": sort}
        res = es_aliyun_util.search(index=index_name, doc_type='_doc', body=body)

        if res['hits']['total'] > 0:
            return res['hits']['total'], res['hits']['hits']

        return 0, []

    @staticmethod
    def deleteSeWorkProjectById(project_id):
        es_aliyun_util.delete("se_work", "_doc", id=project_id)

    @staticmethod
    def querySeEcoTaskById(task_id):
        index_name = "se_eco_partner"
        query = {
            "match": {
                "_id": task_id
            }
        }

        body = {"query": query}
        res = es_aliyun_util.search(index=index_name, doc_type='_doc', body=body)
        if res['hits']['total'] > 0:
            return res['hits']['hits'][0]['_source']
        return

    @staticmethod
    def querySeEcoSubTaskById(main_task_id, sub_task_id):
        index_name = "se_eco_partner"
        query = {
            "bool": {
                "must": [
                    {"match": {"_id": main_task_id}},
                    {"nested": {"path": "sub_tasks", "query": {"match": {"sub_tasks.id": sub_task_id}}}}
                ]
            }
        }

        body = {"query": query}
        res = es_aliyun_util.search(index=index_name, doc_type='_doc', body=body)
        if res['hits']['total'] > 0:
            return res['hits']['hits'][0]['_source']
        return

    @staticmethod
    def querySeEcoPartnerByFilter(user_ids, **parmas) -> (int, list):
        index_name = "se_eco_partner"

        query = {"bool": {"must_not": {"match": {"status": "Deleted"}}, "must": []}}
        user_match = {"bool": {"should": []}}
        if user_ids:
            if user_ids[0] == "*":
                user_match["bool"]["should"].append({"wildcard": {"created_by_id": user_ids[0]}})
            else:
                if not (parmas.get("owner_id") and parmas.get("created_by_id")) and not parmas.get("participants"):
                    user_match["bool"]["should"].append({"terms": {"participant_ids": user_ids}})
                user_match["bool"]["should"].append({"terms": {"created_by_id": user_ids}})
                user_match["bool"]["should"].append({"terms": {"owner_id": user_ids}})
        query["bool"]["must"] = [user_match]

        if parmas.get("participants"):
            participant = {"bool": {"should": []}}
            participant["bool"]["should"].append({"terms": {"participant_ids": parmas.get("participants")}})

            if query["bool"].get("must"):
                query["bool"]["must"].append(participant)
            else:
                query["bool"]["must"] = [participant]

        if parmas.get("created_by_id"):
            create_by_user = {"bool": {"should": []}}
            create_by_user["bool"]["should"].append({"terms": {"created_by_id": parmas.get("created_by_id")}})

            if query["bool"].get("must"):
                query["bool"]["must"].append(create_by_user)
            else:
                query["bool"]["must"] = [create_by_user]

        if parmas.get("owner_id"):
            owner_user = {"bool": {"should": []}}
            owner_user["bool"]["should"].append({"terms": {"owner_id": parmas.get("owner_id")}})

            if query["bool"].get("must"):
                query["bool"]["must"].append(owner_user)
            else:
                query["bool"]["must"] = [owner_user]

        if parmas.get("partner_id"):
            owner_user = {"bool": {"should": [{"match": {"partner_id": parmas.get("partner_id")}}]}}

            if query["bool"].get("must"):
                query["bool"]["must"].append(owner_user)
            else:
                query["bool"]["must"] = [owner_user]

        if parmas.get("query"):
            project_fields = ["subject", "task_number", "contact_info", "partner_name", "partner_contact",
                              "partner_contact_info"]
            project_match = [{"match_phrase": {field: {"query": parmas.get("query"), "slop": 2}}} for field in
                             project_fields]

            task_fields = [
                "record.record_content.content", "sub_tasks.subject", "sub_tasks.task_number",
                "sub_tasks.contact_info", "sub_tasks.partner_contact", "sub_tasks.partner_contact_info"
            ]
            task_match = {
                "nested": {
                    "path": "sub_tasks",
                    "query": {
                        "bool": {
                            "should": [{"match_phrase": {field: {"query": parmas.get("query"), "slop": 2}}} for field in
                                       task_fields]
                        }
                    }
                }
            }

            record_fields = ["sub_tasks.record.record_content.content"]
            record_match = {
                "nested": {
                    "path": "sub_tasks",
                    "query": {
                        "nested": {
                            "path": "sub_tasks.record",
                            "query": {
                                "bool": {
                                    "should": [{"match_phrase": {field: {"query": parmas.get("query"), "slop": 2}}} for
                                               field in record_fields]
                                }
                            }
                        }
                    }
                }
            }

            query_match = {"bool": {"should": [project_match, task_match, record_match]}}
            if query["bool"].get("must"):
                query["bool"]["must"].append(query_match)
            else:
                query["bool"]["must"] = [query_match]

        if parmas.get("date_range"):
            query["bool"]["filter"] = [{
                "range": {
                    "created_date": {
                        "gte": parmas.get("date_range")[0],
                        "lte": parmas.get("date_range")[1],
                        "format": "yyyy-MM-dd HH:mm:ss"
                    }
                }
            }]

        if parmas.get("update_date_range"):
            query["bool"]["filter"] = [{
                "range": {
                    "last_modified_date": {
                        "gte": parmas.get("update_date_range")[0],
                        "lte": parmas.get("update_date_range")[1],
                        "format": "yyyy-MM-dd HH:mm:ss"
                    }
                }
            }]

        sort = [{"created_date": {"order": "desc"}}]
        if parmas.get("order_column") and parmas.get("order_direct"):
            sort = [{parmas.get("order_column"): {"order": parmas.get("order_direct")}}]

        if parmas.get("status"):
            status_match = {"bool": {"should": []}}
            for status in parmas.get("status"):
                status_match["bool"]["should"].append({"match": {"status": status}})

            if query["bool"].get("must"):
                query["bool"]["must"].append(status_match)
            else:
                query["bool"]["must"] = [status_match]

        if 'filter' in query["bool"].keys() and len(query["bool"].keys()) == 1:
            query["bool"] = {"must": [{"match_all": {}}]}

        size = parmas.get("size") if parmas.get("size") else 1000
        page = parmas.get("page") if parmas.get("page") else 1
        body = {"query": query, "size": size, "from": size * (page - 1), "sort": sort}
        res = es_aliyun_util.search(index=index_name, doc_type='_doc', body=body)

        if res['hits']['total'] > 0:
            return res['hits']['total'], res['hits']['hits']

        return 0, []

    @staticmethod
    def deleteSeEcoTaskById(task_id):
        try:
            es_aliyun_util.delete("se_eco_partner", "_doc", id=task_id)
        except exceptions.NotFoundError:
            return

    @staticmethod
    def querySysResourceById(_id):
        index_name = "tech_resource"
        query = {
            "bool": {
                "must": [
                    {"match": {"_id": _id}},
                ]
            }
        }

        body = {"query": query}
        res = es_util.search(index=index_name, doc_type='_doc', body=body)
        if res['hits']['total'] > 0:
            return res['hits']['hits'][0]['_source']
        return

    @staticmethod
    def upsertSysResourceById(_id, doc):
        index_name = "tech_resource"
        es_util.update(index=index_name, doc_type='_doc', body={"doc": doc, "doc_as_upsert": True}, id=_id)

    @staticmethod
    def updateSysResourceById(_id, doc):
        index_name = "tech_resource"
        source_list = [f"ctx._source.{key}=params.{key}" for key in doc.keys()]
        body = {
            "query": {
                "term": {"_id": _id}
            },
            "script": {
                "source": ";".join(source_list),
                "params": doc
            }
        }
        es_util.update_by_query(index=index_name, doc_type='_doc', body=body)

    @staticmethod
    def querySysResource(meta, description, page=1, size=10) -> (int, list):
        index_name = "tech_resource"

        should = []
        if meta:
            for m in meta.split(";"):
                should.append({"wildcard": {"meta": f'*{m}*'}})
        if description:
            should.append({"match_phrase": {"description": {"query": description, "slop": 2}}})

        if should:
            query = {
                "bool": {
                    "should": should,
                    "minimum_should_match": 1
                }
            }
        else:
            query = {"match_all": {}}

        sort = [{"created_date": {"order": "desc"}}]
        body = {"query": query, "size": size, "from": size * (page - 1), "sort": sort}
        res = es_util.search(index=index_name, doc_type='_doc', body=body)

        data = []
        total = res['hits']['total']
        for account in res['hits']['hits']:
            data.append(account['_source'])

        return total, data

    @staticmethod
    def querySeProjectByProjectId(project_id):
        index_name = "se_project"
        query = {"term": {"_id": project_id}}

        body = {"query": query}
        res = es_aliyun_util.search(index=index_name, doc_type='_doc', body=body)
        if res['hits']['total'] > 0:
            return res['hits']['hits'][0]['_source']

        return

    @staticmethod
    def querySeProjectByFilter(user_ids, **parmas) -> (int, list):
        index_name = "se_project"
        query = {"bool": {}}
        user_match = {"bool": {"should": []}}
        if user_ids:
            if user_ids[0] == "*":
                user_match["bool"]["should"].append({"wildcard": {"created_by_id": user_ids[0]}})
            else:
                if parmas.get("classification") not in ['participant', 'favor']:
                    user_match["bool"]["should"].append({"terms": {"created_by_id": user_ids}})
                    user_match["bool"]["should"].append({"terms": {"owner_id": user_ids}})
                if parmas.get("classification") == 'all':
                    user_match["bool"]["should"].append({"terms": {"participant_ids": user_ids}})
        else:
            user_match["bool"]['should'] = [{"term": {"created_by_id": parmas.get("user_id")}},
                                            {"term": {"owner_id": parmas.get("user_id")}}]
        query["bool"]["must"] = [user_match]

        if parmas.get("status"):
            status_match = {"bool": {"should": []}}
            for status in parmas.get("status"):
                status_match["bool"]["should"].append({"match": {"status": status}})

            if query["bool"].get("must"):
                query["bool"]["must"].append(status_match)
            else:
                query["bool"]["must"] = [status_match]

        if parmas.get("task_result"):
            task_result_match = {"bool": {"should": []}}
            for task_result in parmas.get("task_result"):
                task_result_match["bool"]["should"].append({"match": {"task_result": task_result}})

            if query["bool"].get("must"):
                query["bool"]["must"].append(task_result_match)
            else:
                query["bool"]["must"] = [task_result_match ]
                
        if parmas.get("classification"):
            classification = {"bool": {"should": [], "must": [], "must_not": []}}
            if parmas.get("classification") == 'mine':  # 我负责
                classification["bool"]["must"].append({"term": {"owner_id": parmas.get("user_id")}})
            elif parmas.get("classification") == 'participant':  # 我参与
                classification["bool"]["must"].append({"terms": {"participant_ids": [parmas.get("user_id")]}})
                classification["bool"]["must_not"].append({"term": {"owner_id": parmas.get("user_id")}})
            elif parmas.get("classification") == 'subordinate':  # 我下属
                classification["bool"]["should"].append({"terms": {"created_by_id": parmas.get("subordinate_uid")}})
                classification["bool"]["should"].append({"terms": {"owner_id": parmas.get("subordinate_uid")}})
            elif parmas.get("classification") == 'favor':  # 我关注
                classification["bool"]["must"].append({"terms": {"id": parmas.get("project_ids")}})
            elif parmas.get("classification") == 'support':  # 我关注
                classification["bool"]["must"].append({"term": {"is_big_project_support": "是"}})
            elif parmas.get("classification") == 'archive':  # 归档
                if "status" in parmas.keys():
                    parmas.pop("status")
                classification["bool"]["must"].append({"term": {'status': 3}})
            else:  # 默认：全部
                # classification["bool"]["must"].append({"match_all": {}})
                # classification["bool"]["should"].append({"terms": {"id": parmas.get("project_ids")}})
                pass

            if query["bool"].get("must"):
                query["bool"]["must"].append(classification)
            else:
                query["bool"]["must"] = [classification]

        if parmas.get("participants"):
            participant = {"bool": {"should": []}}
            participant["bool"]["should"].append({"terms": {"participant_ids": parmas.get("participants")}})

            if query["bool"].get("must"):
                query["bool"]["must"].append(participant)
            else:
                query["bool"]["must"] = [participant]

        if parmas.get("created_by_id"):
            create_by_user = {"bool": {"should": []}}
            create_by_user["bool"]["should"].append({"terms": {"created_by_id": parmas.get("created_by_id")}})

            if query["bool"].get("must"):
                query["bool"]["must"].append(create_by_user)
            else:
                query["bool"]["must"] = [create_by_user]

        if parmas.get("owner_id"):
            owner_user = {"bool": {"should": []}}
            owner_user["bool"]["should"].append({"terms": {"owner_id": parmas.get("owner_id")}})

            if query["bool"].get("must"):
                query["bool"]["must"].append(owner_user)
            else:
                query["bool"]["must"] = [owner_user]

        if parmas.get("query"):
            project_fields = [
                "subject", "account_name", "contact_info", "contact_name", "project_number", "customer_requirement",
                "opportunity_name", "opportunity_number"
            ]
            project_match = [
                {"match_phrase": {field: {"query": parmas.get("query"), "slop": 2}}} for field in project_fields
            ]

            task_fields = ["tasks.subject", "tasks.account_name", "tasks.contact_info", "tasks.contact_name",
                           "tasks.task_number", "tasks.event_number", "tasks.assign_number"]
            task_match = {
                "nested": {
                    "path": "tasks",
                    "query": {
                        "bool": {
                            "should": [{"match_phrase": {
                                field: {"query": parmas.get("query"), "slop": 2}}} for field in task_fields]
                        }
                    }
                }
            }

            record_fields = ["tasks.record.record_content.content"]
            record_match = {
                "nested": {
                    "path": "tasks",
                    "query": {
                        "nested": {
                            "path": "tasks.record",
                            "query": {
                                "bool": {
                                    "should": [{"match_phrase": {
                                        field: {"query": parmas.get("query"), "slop": 2}}} for field in record_fields]
                                }
                            }
                        }
                    }
                }
            }

            query_match = {"bool": {"should": [project_match, task_match, record_match]}}
            if query["bool"].get("must"):
                query["bool"]["must"].append(query_match)
            else:
                query["bool"]["must"] = [query_match]

        if parmas.get("date_range"):
            query["bool"]["filter"] = [{
                "range": {
                    "created_date": {
                        "gte": datetimeReducedEightHour(time_str=parmas.get("date_range")[0]),
                        "lte": datetimeReducedEightHour(time_str=parmas.get("date_range")[1]),
                        "format": "yyyy-MM-dd HH:mm:ss"
                    }
                }
            }]

        if parmas.get("update_date_range"):
            query["bool"]["filter"] = [{
                "range": {
                    "last_modified_date": {
                        "gte": datetimeReducedEightHour(parmas.get("update_date_range")[0]),
                        "lte": datetimeReducedEightHour(parmas.get("update_date_range")[1]),
                        "format": "yyyy-MM-dd HH:mm:ss"
                    }
                }
            }]

        if parmas.get("last_record_support_start_date_range"):
            query["bool"]["filter"] = [{
                "range": {
                    "last_record_support_start_date": {
                        "gte": parmas.get("last_record_support_start_date_range")[0],
                        "lte": parmas.get("last_record_support_start_date_range")[1],
                        "format": "yyyy-MM-dd HH:mm:ss"
                    }
                }
            }]

        if parmas.get("last_record_created_date_range"):
            query["bool"]["filter"] = [{
                "range": {
                    "last_record_created_date": {
                        "gte": datetimeReducedEightHour(time_str=parmas.get("last_record_created_date_range")[0]),
                        "lte": datetimeReducedEightHour(time_str=parmas.get("last_record_created_date_range")[1]),
                        "format": "yyyy-MM-dd HH:mm:ss"
                    }
                }
            }]

        sort = [{"created_date": {"order": "desc"}}]
        if parmas.get("order_column") and parmas.get("order_direct"):
            sort = [{parmas.get("order_column"): {"order": parmas.get("order_direct")}}]


        if 'filter' in query["bool"].keys() and len(query["bool"].keys()) == 1:
            query["bool"] = {"must": [{"match_all": {}}]}

        size = parmas.get("size") if parmas.get("size") else 1000
        page = parmas.get("page") if parmas.get("page") else 1
        body = {"query": query, "size": size, "from": size * (page - 1), "sort": sort, "_source": True}


        res = es_aliyun_util.search(index=index_name, doc_type='_doc', body=body)
        if res['hits']['total'] > 0:
            return res['hits']['total'], res['hits']['hits']

        return 0, []

    @staticmethod
    def deleteSeProjectProjectById(project_id):
        es_aliyun_util.delete("se_project", "_doc", id=project_id)

