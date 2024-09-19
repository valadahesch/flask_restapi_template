SEWORK_TEMPLATE = [
    {
        "key": "ChannelSupportInternal",
        "name": "渠道支持（内部）",
        "parent_key": ""
    },
    {
        "key": "ChannelTraining",
        "name": "渠道培训",
        "parent_key": "ChannelSupportInternal",
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
                "key": "BusinessOpportunityMining",
                "name": "商机挖掘",
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
        "parent_key": "ChannelSupportInternal",
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
        "key": "ChannelMeetingSupport",
        "name": "渠道会议支持",
        "parent_key": "ChannelSupportInternal",
        "record_struct": [
            {
                "key": "MeetingTheme",
                "name": "会议主题",
                "required": True,
                "type": "input",
                "content": "",
                "index": 1
            },
            {
                "key": "Participants",
                "name": "参会对象",
                "required": True,
                "type": "input",
                "content": "",
                "index": 2
            },
            {
                "key": "NumberOfParticipants",
                "name": "参会人数",
                "required": True,
                "type": "input",
                "content": "",
                "index": 3
            },
            {
                "key": "MainMeetingContent",
                "name": "会议主要内容",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 4
            },
            {
                "key": "Tip",
                "name": "如有编写会议ppt等材料，需要提交相关交流材料",
                "required": False,
                "type": "tip",
                "content": "",
                "index": 5
            }
        ]
    },
    {
        "key": "SalesEmpowerment",
        "name": "销售赋能",
        "parent_key": ""
    },
    {
        "key": "SalesToolProduction",
        "name": "销售工具制作",
        "parent_key": "SalesEmpowerment",
        "record_struct": [
            {
                "key": "ToolProductionProgress",
                "name": "销售工具制作完成进度",
                "required": True,
                "type": "input_number",
                "content": "",
                "dependence": "progress_100",
                "index": 1
            },
            {
                "key": "ToolContentDescription",
                "name": "销售工具内容说明",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 2
            },
            {
                "key": "Tip",
                "name": "如进度为100%，则要求必须提交相关工具附件",
                "required": False,
                "type": "tip",
                "content": "",
                "index": 3
            }
        ]
    },
    {
        "key": "InternalSalesTraining",
        "name": "内部销售培训",
        "parent_key": "SalesEmpowerment",
        "record_struct": [
            {
                "key": "SalesPersonnelInformation",
                "name": "参加销售人员信息",
                "required": True,
                "type": "input",
                "content": "",
                "index": 1
            },
            {
                "key": "TrainingPurpose",
                "name": "培训目的",
                "required": True,
                "type": "input",
                "content": "",
                "index": 2
            },
            {
                "key": "TrainingContent",
                "name": "培训内容",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 3
            },
            {
                "key": "TrainingFeedback",
                "name": "培训反馈",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 4
            },
            {
                "key": "Tip",
                "name": "如有编写培训材料，需要提交相关交流材料",
                "required": False,
                "type": "tip",
                "content": "",
                "index": 5
            }
        ]
    },
    {
        "key": "TrainingEmpowermentInternal",
        "name": "培训赋能（内部）",
        "parent_key": ""
    },
    {
        "key": "AttendProductAndIndustryTraining",
        "name": "参加产品技术及行业培训",
        "parent_key": "TrainingEmpowermentInternal",
        "record_struct": [
            {
                "key": "TrainingContent",
                "name": "培训内容",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 1
            },
            {
                "key": "Trainer",
                "name": "培训讲师",
                "required": True,
                "type": "input",
                "content": "",
                "index": 2
            },
            {
                "key": "TrainingSummary",
                "name": "培训总结",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 3
            },
            {
                "key": "TrainingFeedback",
                "name": "培训建议反馈",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 4
            },
            {
                "key": "Tip",
                "name": "如有编写培训材料，需要提交相关交流材料",
                "required": False,
                "type": "tip",
                "content": "",
                "index": 5
            }
        ]
    },
    {
        "key": "EmpowermentTrainingAndSpeech",
        "name": "赋能培训授课演讲",
        "parent_key": "TrainingEmpowermentInternal",
        "record_struct": [
            {
                "key": "TrainingContent",
                "name": "培训内容",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 1
            },
            {
                "key": "TrainingObject",
                "name": "培训对象",
                "required": True,
                "type": "input",
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
                "key": "TrainingEffect",
                "name": "培训效果",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 4
            },
            {
                "key": "TrainingFeedback",
                "name": "培训建议反馈",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 5
            },
            {
                "key": "Tip",
                "name": "如有编写培训材料，需要提交相关交流材料",
                "required": False,
                "type": "tip",
                "content": "",
                "index": 6
            }
        ]
    },
    {
        "key": "OtherEmpowermentTraining",
        "name": "其他赋能培训",
        "parent_key": "TrainingEmpowermentInternal",
        "record_struct": [
            {
                "key": "TrainingContent",
                "name": "培训内容",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 1
            },
            {
                "key": "Trainer",
                "name": "培训讲师",
                "required": True,
                "type": "input",
                "content": "",
                "index": 2
            },
            {
                "key": "TrainingSummary",
                "name": "培训总结",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 3
            },
            {
                "key": "TrainingFeedback",
                "name": "培训建议反馈",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 4
            },
            {
                "key": "Tip",
                "name": "如有编写培训材料，需要提交相关交流材料",
                "required": False,
                "type": "tip",
                "content": "",
                "index": 6
            }
        ]
    },
    {
        "key": "SEInternalAffairs",
        "name": "SE内部事务",
        "parent_key": ""
    },
    {
        "key": "InternalTeamMeetings",
        "name": "内部团队例会",
        "parent_key": "SEInternalAffairs",
        "record_struct": [
            {
                "key": "MeetingTheme",
                "name": "例会主题",
                "required": True,
                "type": "input",
                "content": "",
                "index": 1
            },
            {
                "key": "Participants",
                "name": "参会对象",
                "required": True,
                "type": "input",
                "content": "",
                "index": 2
            },
            {
                "key": "PersonalSpeechInMeeting",
                "name": "会议发言内容（个人）",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 3
            },
            {
                "key": "OtherRemarks",
                "name": "其他说明",
                "required": False,
                "type": "text_area",
                "content": "",
                "index": 4
            },
            {
                "key": "Tip",
                "name": "如有编写会议分享ppt等材料，需要提交相关交流材料",
                "required": False,
                "type": "tip",
                "content": "",
                "index": 5
            }
        ]
    },
    {
        "key": "InternalTeamManagementCommunication",
        "name": "内部团队管理沟通",
        "parent_key": "SEInternalAffairs",
        "record_struct": [
            {
                "key": "ManagementCommunicationObject",
                "name": "管理沟通对象",
                "required": True,
                "type": "input",
                "content": "",
                "index": 1
            },
            {
                "key": "ManagementCommunicationPurpose",
                "name": "沟通管理目的",
                "required": True,
                "type": "input",
                "content": "",
                "index": 2
            },
            {
                "key": "ManagementCommunicationResult",
                "name": "沟通管理结果",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 3
            },
            {
                "key": "SubsequentPlan",
                "name": "后续计划",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 4
            },
            {
                "key": "OtherRemarks",
                "name": "其他说明",
                "required": False,
                "type": "text_area",
                "content": "",
                "index": 5
            },
            {
                "key": "Tip",
                "name": "如有编写沟通管理材料，需要提交相关交流材料",
                "required": False,
                "type": "tip",
                "content": "",
                "index": 6
            }
        ]
    },
    {
        "key": "SEInternalSharingLearning",
        "name": "SE内部分享学习",
        "parent_key": "SEInternalAffairs",
        "record_struct": [
            {
                "key": "SharingLearningContent",
                "name": "分享学习内容",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 1
            },
            {
                "key": "AdviceOrFeedbackForTraining",
                "name": "针对本次培训学习建议或感想",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 2
            },
            {
                "key": "SubsequentPlan",
                "name": "后续计划",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 3
            },
            {
                "key": "OtherRemarks",
                "name": "其他说明",
                "required": False,
                "type": "text_area",
                "content": "",
                "index": 4
            },
            {
                "key": "Tip",
                "name": "如有编写分享材料，需要提交相关交流材料",
                "required": False,
                "type": "tip",
                "content": "",
                "index": 5
            }
        ]
    },
    {
        "key": "ProductFeatureSchemeVerificationTesting",
        "name": "产品功能方案验证测试",
        "parent_key": "SEInternalAffairs",
        "record_struct": [
            {
                "key": "ProductTypeAndModel",
                "name": "产品类型和具体型号",
                "required": True,
                "type": "input",
                "content": "",
                "index": 1
            },
            {
                "key": "VerificationTestingPurpose",
                "name": "验证测试目的",
                "required": True,
                "type": "input",
                "content": "",
                "index": 2
            },
            {
                "key": "VerificationTestingEffect",
                "name": "验证测试效果",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 3
            },
            {
                "key": "SubsequentPlan",
                "name": "后续计划",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 4
            },
            {
                "key": "Tip",
                "name": "如有编写测试验证材料，需要提交相关交流材料",
                "required": False,
                "type": "tip",
                "content": "",
                "index": 5
            }
        ]
    },
    {
        "key": "NewEmployeeTraining",
        "name": "新员工培训",
        "parent_key": "SEInternalAffairs",
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
                "key": "TrainingContent",
                "name": "培训内容",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 2
            },
            {
                "key": "TrainingEffectAndSuggestions",
                "name": "培训效果和建议",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 3
            },
            {
                "key": "SubsequentPlan",
                "name": "后续计划",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 4
            },
            {
                "key": "OtherRemarks",
                "name": "其他说明",
                "required": False,
                "type": "text_area",
                "content": "",
                "index": 5
            },
            {
                "key": "Tip",
                "name": "如有编写培训材料，需要提交相关交流材料",
                "required": False,
                "type": "tip",
                "content": "",
                "index": 6
            }
        ]
    },
    {
        "key": "PersonnelRecruitment",
        "name": "人员招聘",
        "parent_key": "SEInternalAffairs",
        "record_struct": [
            {
                "key": "RecruitmentPosition",
                "name": "招聘岗位",
                "required": True,
                "type": "input",
                "content": "",
                "index": 1
            },
            {
                "key": "RecruitmentResult",
                "name": "招聘结果",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 2
            },
            {
                "key": "OtherRemarks",
                "name": "其他说明",
                "required": False,
                "type": "text_area",
                "content": "",
                "index": 3
            },
            {
                "key": "Tip",
                "name": "提交应聘人员简历和面试评价等信息",
                "required": False,
                "type": "tip",
                "content": "",
                "index": 4
            }
        ]
    },
    {
        "key": "JobKnowledgeLearningAndResearch",
        "name": "岗位知识学习与研究",
        "parent_key": "SEInternalAffairs",
        "record_struct": [
            {
                "key": "KnowledgeLearningContentSummary",
                "name": "知识学习内容概要总结",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 1
            },
            {
                "key": "OtherRemarks",
                "name": "其他说明",
                "required": False,
                "type": "text_area",
                "content": "",
                "index": 2
            },
            {
                "key": "Tip",
                "name": "如有相关学习材料文件，需要提交相关材料附件",
                "required": False,
                "type": "tip",
                "content": "",
                "index": 3
            }
        ]
    },
    {
        "key": "MarketMeetingSupport",
        "name": "市场会议支持",
        "parent_key": "SEInternalAffairs",
        "record_struct": [
            {
                "key": "MeetingTheme",
                "name": "会议主题",
                "required": True,
                "type": "input",
                "content": "",
                "index": 1
            },
            {
                "key": "Participants",
                "name": "参会对象",
                "required": True,
                "type": "input",
                "content": "",
                "index": 2
            },
            {
                "key": "NumberOfParticipants",
                "name": "参会人数",
                "required": True,
                "type": "input",
                "content": "",
                "index": 3
            },
            {
                "key": "MainMeetingContent",
                "name": "会议主要内容",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 4
            },
            {
                "key": "OtherRemarks",
                "name": "其他说明",
                "required": False,
                "type": "text_area",
                "content": "",
                "index": 5
            },
            {
                "key": "Tip",
                "name": "如有编写会议ppt等材料，需要提交相关交流材料",
                "required": False,
                "type": "tip",
                "content": "",
                "index": 6
            }
        ]
    },
    {
        "key": "OtherSupport",
        "name": "其他支持",
        "parent_key": "SEInternalAffairs",
        "record_struct": [
            {
                "key": "SupportContentDescription",
                "name": "支持内容说明",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 1
            },
            {
                "key": "OtherRemarks",
                "name": "其他说明",
                "required": False,
                "type": "text_area",
                "content": "",
                "index": 2
            },
            {
                "key": "Tip",
                "name": "如有相关材料，需要提交相关材料附件",
                "required": False,
                "type": "tip",
                "content": "",
                "index": 3
            }
        ]
    },
    {
        "key": "CompetitionAnalysis",
        "name": "竞争分析",
        "parent_key": ""
    },
    {
        "key": "CompilationCompetitiveAnalysisMaterials",
        "name": "竞争分析材料编写",
        "parent_key": "CompetitionAnalysis",
        "record_struct": [
            {
                "key": "ProductType",
                "name": "产品类型",
                "required": True,
                "type": "input",
                "content": "",
                "index": 1
            },
            {
                "key": "CompetitiveBrand",
                "name": "竞争对比品牌",
                "required": True,
                "type": "input",
                "content": "",
                "index": 2
            },
            {
                "key": "CompetitiveAnalysisPurpose",
                "name": "竞争分析目的",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 3
            },
            {
                "key": "CompetitiveAnalysisContent",
                "name": "竞争分析内容",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 4
            },
            {
                "key": "CompetitiveAnalysisResults",
                "name": "竞争分析结果",
                "required": False,
                "type": "text_area",
                "content": "",
                "index": 5
            },
            {
                "key": "Tip",
                "name": "提交竞争分析资料和成果",
                "required": False,
                "type": "tip",
                "content": "",
                "index": 6
            }
        ]
    }
]


def getSeWorkProjectType(key):
    value = SEWORK_TEMPLATE
    for v in value:
        if key == v["key"]:
            res = {"key": v["key"], "name": v["name"], "parent_key": v["parent_key"]}
            return res
    return

