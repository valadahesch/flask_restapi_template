ECOPARTNER_TEMPLATE = [
    {
        "key": "EcologicalAllianceSupport",
        "name": "生态联盟支持",
        "parent_key": ""
    },
    {
        "key": "ChannelTraining",
        "name": "渠道培训",
        "parent_key": "EcologicalAllianceSupport",
        "record_struct": [
            {
                "key": "TrainingObject",
                "name": "培训对象",
                "required": True,
                "type": "input",
                "content": "",
                "index": 1
            },
            {
                "key": "TrainingParticipants",
                "name": "培训人数",
                "required": True,
                "type": "input_number",
                "content": "",
                "index": 2
            },
            {
                "key": "TrainingPurpose",
                "name": "培训目的",
                "required": True,
                "type": "input",
                "content": "",
                "index": 3
            },
            {
                "key": "TrainingContent",
                "name": "培训内容",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 4
            },
            {
                "key": "TrainingFeedback",
                "name": "培训反馈",
                "required": False,
                "type": "text_area",
                "content": "",
                "index": 5
            },
            {
                "key": "Tip",
                "name": "要求提交渠道培训的PPT相关材料",
                "required": False,
                "type": "tip",
                "content": "",
                "index": 6
            }
        ]
    },
    {
        "key": "ChannelTechExchange",
        "name": "渠道技术交流",
        "parent_key": "EcologicalAllianceSupport",
        "record_struct": [
            {
                "key": "ExchangeObject",
                "name": "交流对象",
                "required": True,
                "type": "input",
                "content": "",
                "index": 1
            },
            {
                "key": "ExchangePurpose",
                "name": "交流目的",
                "required": True,
                "type": "input",
                "content": "",
                "index": 2
            },
            {
                "key": "ExchangeContent",
                "name": "交流内容记录",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 3
            },
            {
                "key": "ExchangeResult",
                "name": "交流结果",
                "required": True,
                "type": "input",
                "content": "",
                "index": 4
            },
            {
                "key": "RemainingIssues",
                "name": "遗留问题",
                "required": False,
                "type": "text_area",
                "content": "",
                "index": 5
            },
            {
                "key": "Tip",
                "name": "如有编写交流ppt等材料，需要提交相关交流材料",
                "required": False,
                "type": "tip",
                "content": "",
                "index": 6
            }
        ]
    },
    {
        "key": "ChannelTechnicalSupport",
        "name": "渠道技术支持",
        "parent_key": "EcologicalAllianceSupport",
        "record_struct": [
            {
                "key": "SupportedObjects",
                "name": "客户名称",
                "required": True,
                "type": "input",
                "content": "",
                "index": 1
            },
            {
                "key": "SupportNeeds",
                "name": "支持需求",
                "required": True,
                "type": "input",
                "content": "",
                "index": 2
            },
            {
                "key": "SupportContent",
                "name": "支持内容",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 3
            },
            {
                "key": "NextStepPlain",
                "name": "下一步计划",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 4
            }
        ]
    },
    {
        "key": "OEMTransactionSupport",
        "name": "OEM事务支持",
        "parent_key": "EcologicalAllianceSupport",
        "record_struct": [
            {
                "key": "OEMObject",
                "name": "OEM对象",
                "required": True,
                "type": "input",
                "content": "",
                "index": 1
            },
            {
                "key": "SupportNeeds",
                "name": "支持需求",
                "required": True,
                "type": "input",
                "content": "",
                "index": 2
            },
            {
                "key": "SupportContent",
                "name": "支持内容",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 3
            },
            {
                "key": "NextStepPlain",
                "name": "下一步计划",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 4
            }
        ]
    }
]


def getSeEcoTaskType(key):
    value = ECOPARTNER_TEMPLATE
    for v in value:
        if key == v["key"]:
            res = {"key": v["key"], "name": v["name"], "parent_key": v["parent_key"]}
            return res
    return