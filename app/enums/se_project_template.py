SEPROJECT_TEMPLATE = [
    {
        "key": "BusinessOpportunitiesAndBudgetRecognition",
        "name": "商机及预算确认",
        "parent_key": ""
    },
    {
        "key": "PreparationOfProjectInitiationReport",
        "name": "立项报告编写",
        "parent_key": "BusinessOpportunitiesAndBudgetRecognition",
        "record_struct": [
            {
                "key": "SupportSummaryKeyActionRecord",
                "name": "支持总结（关键动作及支持结果记录）",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 1
            },
            {
                "key": "ProjectRisk",
                "name": "项目风险",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 2
            },
            {
                "key": "NextActionPlan",
                "name": "下一步行动计划",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 3
            },
            {
                "key": "ReportProgress",
                "name": "报告完成进度",
                "required": True,
                "type": "input_number",
                "content": "",
                "dependence": "progress_100",
                "index": 4
            },
            {
                "key": "ProjectRequirement",
                "name": "项目需求",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 5
            },
            {
                "key": "RestsTextArea",
                "name": "其他",
                "required": False,
                "type": "text_area",
                "content": "",
                "index": 6
            },
            {
                "content": "",
                "index": 7,
                "key": "Tip",
                "name": "如报告完成进度为100%，则要求必须提交相关报告附件",
                "required": False,
                "type": "tip"
            }
        ]
    },
    {
        "key": "SingleSourceApprovalFormPreparation",
        "name": "单一来源审批表编写",
        "parent_key": "BusinessOpportunitiesAndBudgetRecognition",
        "record_struct": [
            {
                "key": "SupportSummaryKeyActionRecord",
                "name": "支持总结（关键动作及支持结果记录）",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 1
            },
            {
                "key": "ProjectRisk",
                "name": "项目风险",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 2
            },
            {
                "key": "NextActionPlan",
                "name": "下一步行动计划",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 3
            },
            {
                "key": "ReportProgress",
                "name": "报告完成进度",
                "required": True,
                "type": "input_number",
                "content": "",
                "dependence": "progress_100",
                "index": 4
            },
            {
                "key": "ProjectRequirement",
                "name": "项目需求",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 5
            },
            {
                "key": "RestsTextArea",
                "name": "其他",
                "required": False,
                "type": "text_area",
                "content": "",
                "index": 6
            },
            {
                "content": "",
                "index": 7,
                "key": "Tip",
                "name": "如报告完成进度为100%，则要求必须提交相关报告附件",
                "required": False,
                "type": "tip"
            }
        ]
    },
    {
        "key": "RequirementsGatheringAndGuidance",
        "name": "需求收集和引导",
        "parent_key": ""
    },
    {
        "key": "ProjectRequirementResearch",
        "name": "项目需求调研",
        "parent_key": "RequirementsGatheringAndGuidance",
        "record_struct": [
            {
                "key": "SupportSummaryKeyActionRecord",
                "name": "支持总结（关键动作及支持结果记录）",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 1
            },
            {
                "key": "ProjectRisk",
                "name": "项目风险",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 2
            },
            {
                "key": "NextActionPlan",
                "name": "下一步行动计划",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 3
            },
            {
                "key": "ResearchPurpose",
                "name": "调研目的",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 4
            },
            {
                "key": "DetailedRequirementDescription",
                "name": "详细需求说明",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 5
            },
            {
                "key": "RestsTextArea",
                "name": "其他",
                "required": False,
                "type": "text_area",
                "content": "",
                "index": 6
            }
        ]
    },
    {
        "key": "DemandInducing",
        "name": "需求引导",
        "parent_key": "RequirementsGatheringAndGuidance",
        "record_struct": [
            {
                "key": "SupportSummaryKeyActionRecord",
                "name": "支持总结（关键动作及支持结果记录）",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 1
            },
            {
                "key": "ProjectRisk",
                "name": "项目风险",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 2
            },
            {
                "key": "NextActionPlan",
                "name": "下一步行动计划",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 3
            },
            {
                "key": "FriendBusinessInformation",
                "name": "友商情况说明",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 4
            },
            {
                "key": "StatementOfOurWeakness",
                "name": "我方劣势说明",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 5
            },
            {
                "key": "OurAdvantageStatement",
                "name": "我方优势说明",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 6
            },
            {
                "key": "RestsTextArea",
                "name": "其他",
                "required": False,
                "type": "text_area",
                "content": "",
                "index": 7
            }
        ]
    },
    {
        "key": "SolutionPreparationAndSubmission",
        "name": "解决方案编写及提交",
        "parent_key": ""
    },
    {
        "key": "SolutionWriting",
        "name": "解决方案编写",
        "parent_key": "SolutionPreparationAndSubmission",
        "record_struct": [
            {
                "key": "SupportSummaryKeyActionRecord",
                "name": "支持总结（关键动作及支持结果记录）",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 1
            },
            {
                "key": "ProjectRisk",
                "name": "项目风险",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 2
            },
            {
                "key": "NextActionPlan",
                "name": "下一步行动计划",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 3
            },
            {
                "key": "ProjectCompletionSchedule",
                "name": "方案完成进度",
                "required": True,
                "type": "input_number",
                "content": "",
                "dependence": "progress_100",
                "index": 4
            },
            {
                "key": "SolutionUserRequirements",
                "name": "方案用户需求",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 5
            },
            {
                "key": "RestsTextArea",
                "name": "其他",
                "required": False,
                "type": "text_area",
                "content": "",
                "index": 6
            },
            {
                "content": "",
                "index": 7,
                "key": "Tip",
                "name": "如方案完成进度为100%，则要求必须提交相关方案附件",
                "required": False,
                "type": "tip"
            }
        ]
    },
    {
        "key": "ProgramGuidanceAndAdjustment",
        "name": "方案引导及调整",
        "parent_key": "SolutionPreparationAndSubmission",
        "record_struct": [
            {
                "key": "SupportSummaryKeyActionRecord",
                "name": "支持总结（关键动作及支持结果记录）",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 1
            },
            {
                "key": "ProjectRisk",
                "name": "项目风险",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 2
            },
            {
                "key": "NextActionPlan",
                "name": "下一步行动计划",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 3
            },
            {
                "key": "FriendBusinessInformation",
                "name": "友商情况说明",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 4
            },
            {
                "key": "StatementOfOurWeakness",
                "name": "我方劣势说明",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 5
            },
            {
                "key": "OurAdvantageStatement",
                "name": "我方优势说明",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 6
            },
            {
                "key": "RestsTextArea",
                "name": "其他",
                "required": False,
                "type": "text_area",
                "content": "",
                "index": 7
            }
        ]
    },
    {
        "key": "ProductSelectionAndAnalysis",
        "name": "产品选型与分析",
        "parent_key": "SolutionPreparationAndSubmission",
        "record_struct": [
            {
                "key": "SupportSummaryKeyActionRecord",
                "name": "支持总结（关键动作及支持结果记录）",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 1
            },
            {
                "key": "ProjectRisk",
                "name": "项目风险",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 2
            },
            {
                "key": "NextActionPlan",
                "name": "下一步行动计划",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 3
            },
            {
                "key": "ProjectDescription",
                "name": "项目说明",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 4
            },
            {
                "key": "ParameterFingerprintFriendMerchant",
                "name": "参数指纹友商",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 5
            },
            {
                "key": "OurProductSelectionDisadvantageDescription",
                "name": "我方产品选型劣势说明",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 6
            },
            {
                "key": "OurProductSelectionAdvantageDescription",
                "name": "我方产品选型优势说明",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 7
            },
            {
                "key": "RestsTextArea",
                "name": "其他",
                "required": False,
                "type": "text_area",
                "content": "",
                "index": 8
            }
        ]
    },
    {
        "key": "TechnicalExchange",
        "name": "技术交流",
        "parent_key": "SolutionPreparationAndSubmission",
        "record_struct": [
            {
                "key": "SupportSummaryKeyActionRecord",
                "name": "支持总结（关键动作及支持结果记录）",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 1
            },
            {
                "key": "ProjectRisk",
                "name": "项目风险",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 2
            },
            {
                "key": "NextActionPlan",
                "name": "下一步行动计划",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 3
            },
            {
                "key": "Communicatee",
                "name": "交流对象",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 4
            },
            {
                "key": "CommunicativePurpose",
                "name": "交流目的",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 5
            },
            {
                "key": "LeftoverProblem",
                "name": "遗留问题",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 6
            },
            {
                "key": "RestsTextArea",
                "name": "其他",
                "required": False,
                "type": "text_area",
                "content": "",
                "index": 7
            }
        ]
    },
    {
        "key": "POCTest",
        "name": "POC测试",
        "parent_key": ""
    },
    {
        "key": "POCTestTestPlanPreparationAndGuidance",
        "name": "测试方案编写及引导",
        "parent_key": "POCTest",
        "record_struct": [
            {
                "key": "SupportSummaryKeyActionRecord",
                "name": "支持总结（关键动作及支持结果记录）",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 1
            },
            {
                "key": "ProjectRisk",
                "name": "项目风险",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 2
            },
            {
                "key": "NextActionPlan",
                "name": "下一步行动计划",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 3
            },
            {
                "key": "TestTheProgressOfTheSolution",
                "name": "测试方案完成进度",
                "required": True,
                "type": "input_number",
                "content": "",
                "dependence": "progress_100",
                "index": 4
            },
            {
                "key": "TestSchemeDesignPurpose",
                "name": "测试方案设计目的",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 5
            },
            {
                "key": "TestTheProduct",
                "name": "测试产品",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 6
            },
            {
                "key": "MajorCompetitorsAndProgramSpecificTestProjects",
                "name": "主要竞争对手及方案针对性的测试项目",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 7
            },
            {
                "key": "RestsTextArea",
                "name": "其他",
                "required": False,
                "type": "text_area",
                "content": "",
                "index": 8
            },
            {
                "content": "",
                "index": 9,
                "key": "Tip",
                "name": "如方案完成进度为100%，则要求必须提交相关方案附件",
                "required": False,
                "type": "tip"
            }
        ]
    },
    {
        "key": "ProductTestingFunctionalAndPerformanceTesting",
        "name": "产品测试（功能及性能测试）",
        "parent_key": "POCTest",
        "record_struct": [
            {
                "key": "SupportSummaryKeyActionRecord",
                "name": "支持总结（关键动作及支持结果记录）",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 1
            },
            {
                "key": "ProjectRisk",
                "name": "项目风险",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 2
            },
            {
                "key": "NextActionPlan",
                "name": "下一步行动计划",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 3
            },
            {
                "key": "TestPurpose",
                "name": "测试目的",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 4
            },
            {
                "key": "TestEquipmentType",
                "name": "测试设备型号",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 5
            },
            {
                "key": "DeviceHardwareConfiguration",
                "name": "设备硬件配置",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 6
            },
            {
                "key": "DeviceSoftwareVersion",
                "name": "设备软件版本",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 7
            },
            {
                "key": "EquipmentStatus",
                "name": "设备状态",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 8
            },
            {
                "key": "EquipmentOnlineDate",
                "name": "设备上线日期",
                "required": True,
                "type": "input_date",
                "content": "",
                "index": 9
            },
            {
                "key": "AuthorizationExpirationDate",
                "name": "授权到期日期",
                "required": True,
                "type": "input_date",
                "content": "",
                "index": 10
            },
            {
                "key": "DeviceDeploymentLocation",
                "name": "设备部署位置",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 11
            }
        ]
    },
    {
        "key": "TestReportWriting",
        "name": "测试报告编写",
        "parent_key": "POCTest",
        "record_struct": [
            {
                "key": "SupportSummaryKeyActionRecord",
                "name": "支持总结（关键动作及支持结果记录）",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 1
            },
            {
                "key": "ProjectRisk",
                "name": "项目风险",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 2
            },
            {
                "key": "NextActionPlan",
                "name": "下一步行动计划",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 3
            },
            {
                "key": "TestReportCompletionProgress",
                "name": "测试报告完成进度",
                "required": True,
                "type": "input_number",
                "content": "",
                "dependence": "progress_100",
                "index": 4
            },
            {
                "key": "TestIndexUnsatisfactoryItemsAndSolutions",
                "name": "测试指标不满意项及解决方案",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 5
            },
            {
                "key": "RestsTextArea",
                "name": "其他",
                "required": False,
                "type": "text_area",
                "content": "",
                "index": 6
            },
            {
                "content": "",
                "index": 7,
                "key": "Tip",
                "name": "如报告完成进度为100%，则要求必须提交相关报告附件",
                "required": False,
                "type": "tip"
            }
        ]
    },
    {
        "key": "ShortlistingTest",
        "name": "入围测试",
        "parent_key": ""
    },
    {
        "key": "TestPlanPreparationAndGuidance_",
        "name": "测试方案编写及引导",
        "parent_key": "ShortlistingTest",
        "record_struct": [
            {
                "key": "SupportSummaryKeyActionRecord",
                "name": "支持总结（关键动作及支持结果记录）",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 1
            },
            {
                "key": "ProjectRisk",
                "name": "项目风险",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 2
            },
            {
                "key": "NextActionPlan",
                "name": "下一步行动计划",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 3
            },
            {
                "key": "TestTheProgressOfTheSolution",
                "name": "测试方案完成进度",
                "required": True,
                "type": "input_number",
                "content": "",
                "dependence": "progress_100",
                "index": 4
            },
            {
                "key": "TestSchemeDesignPurpose",
                "name": "测试方案设计目的",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 5
            },
            {
                "key": "TestTheProduct",
                "name": "测试产品",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 6
            },
            {
                "key": "MajorCompetitorsAndProgramSpecificTestProjects",
                "name": "主要竞争对手及方案针对性的测试项目",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 7
            },
            {
                "key": "RestsTextArea",
                "name": "其他",
                "required": False,
                "type": "text_area",
                "content": "",
                "index": 8
            },
            {
                "content": "",
                "index": 9,
                "key": "Tip",
                "name": "如方案完成进度为100%，则要求必须提交相关报方案附件",
                "required": False,
                "type": "tip"
            }
        ]
    },
    {
        "key": "ShortlistedTestInitiation",
        "name": "入围测试启动",
        "parent_key": "ShortlistingTest",
        "record_struct": [
            {
                "key": "SupportSummaryKeyActionRecord",
                "name": "支持总结（关键动作及支持结果记录）",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 1
            },
            {
                "key": "ProjectRisk",
                "name": "项目风险",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 2
            },
            {
                "key": "NextActionPlan",
                "name": "下一步行动计划",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 3
            },
            {
                "key": "RestsTextArea",
                "name": "其他",
                "required": False,
                "type": "text_area",
                "content": "",
                "index": 4
            }
        ]
    },
    {
        "key": "ShortlistedTestPreparation",
        "name": "入围测试准备",
        "parent_key": "ShortlistingTest",
        "record_struct": [
            {
                "key": "SupportSummaryKeyActionRecord",
                "name": "支持总结（关键动作及支持结果记录）",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 1
            },
            {
                "key": "ProjectRisk",
                "name": "项目风险",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 2
            },
            {
                "key": "NextActionPlan",
                "name": "下一步行动计划",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 3
            },
            {
                "key": "ItemSegmentType",
                "name": "项目段类型",
                "required": True,
                "type": "input",
                "content": "",
                "index": 4
            },
            {
                "key": "ProjectSegmentTimeNode",
                "name": "项目段时间节点",
                "required": True,
                "type": "input_date",
                "content": "",
                "index": 5
            },
            {
                "key": "EquipmentCategory",
                "name": "设备品类",
                "required": True,
                "type": "input",
                "content": "",
                "index": 6
            },
            {
                "key": "SpecificationOfTechnicalRequirements",
                "name": "典配技术要求",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 7
            },
            {
                "key": "TestEquipmentType",
                "name": "测试设备型号",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 8
            },
            {
                "key": "TestDeviceHardwareInformation",
                "name": "测试设备硬件信息",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 9
            },
            {
                "key": "TestDeviceSoftwareInformation",
                "name": "测试设备软件信息",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 10
            },
            {
                "key": "ShortlistedTestLocationAndInterfaceInformation",
                "name": "入围测试地点及接口人信息",
                "required": False,
                "type": "text_area",
                "content": "",
                "index": 11
            },
            {
                "key": "CheckTheSituationOfFriendsAndInformationFeedback",
                "name": "参测友商情况及信息反馈",
                "required": False,
                "type": "text_area",
                "content": "",
                "index": 12
            },
            {
                "key": "RestsTextArea",
                "name": "其他",
                "required": False,
                "type": "text_area",
                "content": "",
                "index": 13
            }
        ]
    },
    {
        "key": "Prequalification",
        "name": "资格预审",
        "parent_key": "ShortlistingTest",
        "record_struct": [
            {
                "key": "SupportSummaryKeyActionRecord",
                "name": "支持总结（关键动作及支持结果记录）",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 1
            },
            {
                "key": "ProjectRisk",
                "name": "项目风险",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 2
            },
            {
                "key": "NextActionPlan",
                "name": "下一步行动计划",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 3
            },
            {
                "key": "ParticipationInPrequalification",
                "name": "资格预审参与方式",
                "required": True,
                "type": "input",
                "content": "",
                "index": 4
            },
            {
                "key": "FriendBusinessSituation",
                "name": "友商情况",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 5
            },
            {
                "key": "ResultsOfPrequalification",
                "name": "资格预审结果",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 6
            },
            {
                "key": "RestsTextArea",
                "name": "其他",
                "required": False,
                "type": "text_area",
                "content": "",
                "index": 7
            }
        ]
    },
    {
        "key": "FinalistTestImplementation",
        "name": "入围测试实施",
        "parent_key": "ShortlistingTest",
        "record_struct": [
            {
                "key": "SupportSummaryKeyActionRecord",
                "name": "支持总结（关键动作及支持结果记录）",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 1
            },
            {
                "key": "ProjectRisk",
                "name": "项目风险",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 2
            },
            {
                "key": "NextActionPlan",
                "name": "下一步行动计划",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 3
            },
            {
                "key": "ProjectPhaseDailyWorkDescriptionDaily",
                "name": "项目阶段日常工作描述（日常）",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 4
            },
            {
                "key": "ProjectStageRiskEmergencyWarningAndAvoidance",
                "name": "项目阶段风险/突发情况预警及规避",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 5
            },
            {
                "key": "SummaryOfTestResultsAndRemainingProblemsDuringTheProjectPhaseCycle",
                "name": "项目阶段测试结果及遗留问题总结（周期）",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 6
            },
            {
                "key": "Tip",
                "name": "项目阶段资料附件需上传",
                "required": False,
                "type": "tip",
                "content": "",
                "index": 7
            }
        ]
    },
    {
        "key": "BusinessNegotiation",
        "name": "商务谈判",
        "parent_key": "ShortlistingTest",
        "record_struct": [
            {
                "key": "SupportSummaryKeyActionRecord",
                "name": "支持总结（关键动作及支持结果记录）",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 1
            },
            {
                "key": "ProjectRisk",
                "name": "项目风险",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 2
            },
            {
                "key": "NextActionPlan",
                "name": "下一步行动计划",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 3
            },
            {
                "key": "ParticipationInBusinessNegotiations",
                "name": "商务谈判参与方式",
                "required": True,
                "type": "input",
                "content": "",
                "index": 4
            },
            {
                "key": "FriendBusinessSituation",
                "name": "友商情况",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 5
            },
            {
                "key": "OutcomeOfBusinessNegotiation",
                "name": "商务谈判结果",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 6
            },
            {
                "key": "RestsTextArea",
                "name": "其他",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 7
            }
        ]
    },
    {
        "key": "Bid",
        "name": "招投标",
        "parent_key": ""
    },
    {
        "key": "PreBidGuidance",
        "name": "标前引导",
        "parent_key": "Bid",
        "record_struct": [
            {
                "key": "SupportSummaryKeyActionRecord",
                "name": "支持总结（关键动作及支持结果记录）",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 1
            },
            {
                "key": "ProjectRisk",
                "name": "项目风险",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 2
            },
            {
                "key": "NextActionPlan",
                "name": "下一步行动计划",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 3
            },
            {
                "key": "FriendBusinessInformation",
                "name": "友商情况说明",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 4
            },
            {
                "key": "StatementOfOurWeakness",
                "name": "我方劣势说明",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 5
            },
            {
                "key": "OurAdvantageStatement",
                "name": "我方优势说明",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 6
            },
            {
                "key": "RestsTextArea",
                "name": "其他",
                "required": False,
                "type": "text_area",
                "content": "",
                "index": 7
            }
        ]
    },
    {
        "key": "CompilingBiddingParametersAndDesigningScoringCriteria",
        "name": "招标参数编写及评分标准设计",
        "parent_key": "Bid",
        "record_struct": [
            {
                "key": "SupportSummaryKeyActionRecord",
                "name": "支持总结（关键动作及支持结果记录）",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 1
            },
            {
                "key": "ProjectRisk",
                "name": "项目风险",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 2
            },
            {
                "key": "NextActionPlan",
                "name": "下一步行动计划",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 3
            },
            {
                "key": "MaterialCompletionSchedule",
                "name": "材料完成进度",
                "required": True,
                "type": "input_number",
                "dependence": "progress_100",
                "content": "",
                "index": 4
            },
            {
                "key": "ProjectDescription",
                "name": "参数涉及产品型号和数量",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 5
            },
            {
                "key": "RestsTextArea",
                "name": "其他",
                "required": False,
                "type": "text_area",
                "content": "",
                "index": 6
            },
            {
                "content": "",
                "index": 7,
                "key": "Tip",
                "name": "如材料完成进度为100%，则要求必须提交相关材料附件",
                "required": False,
                "type": "tip"
            }
        ]
    },
    {
        "key": "PreparationOfBidMaterials",
        "name": "投标材料编写",
        "parent_key": "Bid",
        "record_struct": [
            {
                "key": "SupportSummaryKeyActionRecord",
                "name": "支持总结（关键动作及支持结果记录）",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 1
            },
            {
                "key": "ProjectRisk",
                "name": "项目风险",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 2
            },
            {
                "key": "NextActionPlan",
                "name": "下一步行动计划",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 3
            },
            {
                "key": "MaterialCompletionSchedule",
                "name": "材料完成进度",
                "required": True,
                "type": "input_number",
                "dependence": "progress_100",
                "content": "",
                "index": 4
            },
            {
                "key": "BiddingType",
                "name": "招标方式",
                "required": True,
                "type": "input",
                "content": "",
                "index": 5
            },
            {
                "key": "BidTime",
                "name": "投标时间",
                "required": True,
                "type": "input_date",
                "content": "",
                "index": 6
            },
            {
                "key": "RestsTextArea",
                "name": "其他",
                "required": False,
                "type": "text_area",
                "content": "",
                "index": 7
            },
            {
                "content": "",
                "index": 7,
                "key": "Tip",
                "name": "如材料完成进度为100%，则要求必须提交相关材料附件",
                "required": False,
                "type": "tip"
            }
        ]
    },
    {
        "key": "OnSiteBiddingAndQA",
        "name": "现场投标及答疑",
        "parent_key": "Bid",
        "record_struct": [
            {
                "key": "SupportSummaryKeyActionRecord",
                "name": "支持总结（关键动作及支持结果记录）",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 1
            },
            {
                "key": "ProjectRisk",
                "name": "项目风险",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 2
            },
            {
                "key": "NextActionPlan",
                "name": "下一步行动计划",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 3
            },
            {
                "key": "BiddingType",
                "name": "招标方式",
                "required": True,
                "type": "input",
                "content": "",
                "index": 4
            },
            {
                "key": "ParticipateInTheBiddingCompanyAndOffer",
                "name": "参与投标公司及报价",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 5
            },
            {
                "key": "WinningCompany",
                "name": "中标公司",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 6
            },
            {
                "key": "RestsTextArea",
                "name": "其他",
                "required": False,
                "type": "text_area",
                "content": "",
                "index": 7
            }
        ]
    },
    {
        "key": "AfterSales",
        "name": "售后事务",
        "parent_key": ""
    },
    {
        "key": "AfterSalesRecord",
        "name": "售后事务",
        "parent_key": "AfterSales",
        "record_struct": [
            {
                "key": "SupportingContentDescriptionRecord",
                "name": "支持内容说明",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 1
            },
            {
                "key": "OtherDescriptionRecord",
                "name": "其他说明",
                "required": False,
                "type": "text_area",
                "content": "",
                "index": 2
            },
            {
                "content": "",
                "index": 3,
                "key": "Tip",
                "name": "如有相关材料，需要提交相关材料附件",
                "required": False,
                "type": "tip"
            }
        ]
    },
    {
        "key": "LargeProjectManagement",
        "name": "大项目管理",
        "parent_key": ""
    },
    {
        "key": "ProjectManagement",
        "name": "项目管理",
        "parent_key": "LargeProjectManagement",
        "record_struct": [
            {
                "key": "SupportSummaryKeyActionRecord",
                "name": "支持总结",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 1
            },
            {
                "key": "ProgressUpdate",
                "name": "进度更新",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 2
            },
            {
                "key": "ProjectRisksTodayIssues",
                "name": "项目风险-今日出现的问题",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 1
            },
            {
                "key": "ProjectRisksIdentifiedRisks",
                "name": "项目风险-已识别风险",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 2
            },
            {
                "key": "NextActionPlan",
                "name": "下一步行动计划",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 3
            },
            {
                "key": "RestsTextArea",
                "name": "其他",
                "required": False,
                "type": "text_area",
                "content": "",
                "index": 4
            }
        ]
    },
    {
        "key": "Rests",
        "name": "其他",
        "parent_key": ""
    },
    {
        "key": "RestsRecord",
        "name": "其他",
        "parent_key": "Rests",
        "record_struct": [
            {
                "key": "SupportSummaryKeyActionRecord",
                "name": "支持总结（关键动作及支持结果记录）",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 1
            },
            {
                "key": "ProjectRisk",
                "name": "项目风险",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 2
            },
            {
                "key": "NextActionPlan",
                "name": "下一步行动计划",
                "required": True,
                "type": "text_area",
                "content": "",
                "index": 3
            },
            {
                "key": "RestsTextArea",
                "name": "其他",
                "required": False,
                "type": "text_area",
                "content": "",
                "index": 4
            }
        ]
    }
]


def getSeProjectProjectType(key):
    value = SEPROJECT_TEMPLATE
    for v in value:
        if key == v["key"]:
            res = {"key": v["key"], "name": v["name"],
                   "parent_key": v["parent_key"]}
            return res
    return
