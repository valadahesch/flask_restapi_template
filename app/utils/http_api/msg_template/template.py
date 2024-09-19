from marshmallow import Schema, post_dump, fields


class Template(Schema):
    __id__ = ''
    __media__ = ''
    __data__ = {}

    def getTemplateId(self):
        return self.__id__

    def getMedia(self):
        return self.__media__

    def getData(self):
        return self.__data__

    def update(self, update):
        self.__data__ = update

    @post_dump
    def setData(self, data, **kwargs):
        self.__data__ = data


class BusinessEmail(Template):
    __id__ = '4539'
    __media__ = 'email'
    crm_owner_name = fields.Str(data_key='ownername')
    lead_code = fields.Str(data_key='lead_name')
    create_by = fields.Str(data_key='caseuser')
    company_name = fields.Str(data_key='companyname')
    contact_name = fields.Str(data_key='fullname')
    contact_way = fields.Str(data_key='phone')
    description = fields.Str(data_key='requiredescribe')
    province = fields.Str()
    city = fields.Str()
    lead_id = fields.Str(data_key='lead_id')


class BusinessWeWork(BusinessEmail):
    __id__ = '4537'
    __media__ = 'wexin_work_app'


class SeWorkProjectEmail(Template):
    __id__ = '5678'
    __media__ = 'email'
    id = fields.Str()
    project_number = fields.Str()
    subject = fields.Str()
    owner_name = fields.Str()
    created_by_name = fields.Str()
    created_date = fields.Str()


class SeWorkTaskEmail(Template):
    __id__ = '5682'
    __media__ = 'email'
    id = fields.Str()
    task_number = fields.Str()
    subject = fields.Str()
    owner_name = fields.Str()
    created_by_name = fields.Str()
    created_date = fields.Str()
    project_id = fields.Str()
    project_number = fields.Str()
    project_subject = fields.Str()


class SeWorkSubTaskEmail(Template):
    __id__ = '5684'
    __media__ = 'email'
    id = fields.Str()
    task_number = fields.Str()
    subject = fields.Str()
    owner_name = fields.Str()
    created_by_name = fields.Str()
    created_date = fields.Str()
    parent_task_number = fields.Str()
    parent_task_subject = fields.Str()
    project_id = fields.Str()
    project_number = fields.Str()
    project_subject = fields.Str()


class SeWorkTaskArchiveEmail(Template):
    __id__ = '5685'
    __media__ = 'email'
    id = fields.Str()
    task_number = fields.Str()
    subject = fields.Str()


class SeWorkProjectArchiveEmail(Template):
    __id__ = '5686'
    __media__ = 'email'
    id = fields.Str()
    project_number = fields.Str()
    subject = fields.Str()


class SeEcoTaskEmail(Template):
    __id__ = '5900'
    __media__ = 'email'
    id = fields.Str()
    task_number = fields.Str()
    subject = fields.Str()
    site_domain = fields.Str()
    owner_name = fields.Str()
    created_by_name = fields.Str()
    created_date = fields.Str()


class SeEcoSubTaskEmail(Template):
    __id__ = '5902'
    __media__ = 'email'
    id = fields.Str()
    task_number = fields.Str()
    subject = fields.Str()
    site_domain = fields.Str()
    owner_name = fields.Str()
    created_by_name = fields.Str()
    created_date = fields.Str()

    parent_task_id = fields.Str()
    parent_task_number = fields.Str()
    parent_task_subject = fields.Str()


class SeEcoAllTaskArchiveEmail(Template):
    __id__ = '5904'
    __media__ = 'email'
    id = fields.Str()
    task_number = fields.Str()
    subject = fields.Str()
    site_domain = fields.Str()


class SeEcoRecordPendingEmail(Template):
    __id__ = '5906'
    __media__ = 'email'
    task_number = fields.Str()
    subject = fields.Str()
    site_domain = fields.Str()
    created_by_name = fields.Str()
    partner_name = fields.Str()
    record_content = fields.Str()
    approver = fields.Str()


class SeEcoRecordApprovedEmail(Template):
    __id__ = '5907'
    __media__ = 'email'
    task_number = fields.Str()
    subject = fields.Str()
    site_domain = fields.Str()
    created_by_name = fields.Str()
    record_content = fields.Str()
    approver = fields.Str()
    partner_name = fields.Str()
    support_type_2nd = fields.Str()
    channel_manager_name = fields.Str()
    published_date = fields.Str()
    support_start_date = fields.Str()
    support_end_date = fields.Str()
    support_duration = fields.Str()


class SeEcoRecordUnApprovedEmail(Template):
    __id__ = '5910'
    __media__ = 'email'
    task_number = fields.Str()
    subject = fields.Str()
    site_domain = fields.Str()
    created_by_name = fields.Str()
    record_content = fields.Str()
    reject_reason = fields.Str()


class SeWorkRecordPendingEmail(Template):
    __id__ = '5520'
    __media__ = 'email'
    task_number = fields.Str()
    subject = fields.Str()
    site_domain = fields.Str()
    created_by_name = fields.Str()
    record_content = fields.Str()
    approver = fields.Str()


class SeWorkRecordApprovedEmail(Template):
    __id__ = '5521'
    __media__ = 'email'
    task_id = fields.Str()
    created_by_name = fields.Str()
    task_number = fields.Str()
    subject = fields.Str()
    site_domain = fields.Str()
    support_type_1st = fields.Str()
    support_type_2nd = fields.Str()
    approver = fields.Str()
    support_start_date = fields.Str()
    support_end_date = fields.Str()
    published_date = fields.Str()
    record_content = fields.Str()



class SeWorkRecordUnApprovedEmail(Template):
    __id__ = '5522'
    __media__ = 'email'
    task_id = fields.Str()
    task_number = fields.Str()
    subject = fields.Str()
    site_domain = fields.Str()
    record_content = fields.Str()
    reject_reason = fields.Str()


class SeProjectProjectFirstEmail(Template):
    __id__ = '6337'
    __media__ = 'email'
    project_id = fields.Str()
    project_number = fields.Str()
    subject = fields.Str()
    owner_name = fields.Str()
    created_by_name = fields.Str()
    created_date = fields.Str()


class SeProjectTaskSecondEmail(Template):
    __id__ = '6339'
    __media__ = 'email'
    project_id = fields.Str()
    project_number = fields.Str()
    task_id = fields.Str()
    task_number = fields.Str()
    subject = fields.Str()
    task_subject = fields.Str()
    owner_name = fields.Str()
    task_owner_name = fields.Str()
    created_by_name = fields.Str()
    created_date = fields.Str()


class SeProjectTaskDispatchFailedEmail(Template):
    __id__ = '6365'
    __media__ = 'email'
    line_name = fields.Str()
    reason = fields.Str()


class SeProjectSubTaskEmail(Template):
    __id__ = '6346'
    __media__ = 'email'
    task_id = fields.Str()
    task_number = fields.Str()
    site_domain = fields.Str()
    subject = fields.Str()
    owner_name = fields.Str()
    created_by_name = fields.Str()
    created_date = fields.Str()
    parent_task_number = fields.Str()
    parent_task_subject = fields.Str()
    project_id = fields.Str()
    project_number = fields.Str()
    project_subject = fields.Str()


class SeProjectRecordPendingEmail(Template):
    __id__ = '6347'
    __media__ = 'email'
    task_number = fields.Str()
    created_by_name = fields.Str()
    partner_name = fields.Str()
    subject = fields.Str()
    site_domain = fields.Str()
    record_content = fields.Str()


class SeProjectRecordApprovedEmail(Template):
    __id__ = '6348'
    __media__ = 'email'
    task_id = fields.Str()
    created_by_name = fields.Str()
    task_number = fields.Str()
    subject = fields.Str()
    site_domain = fields.Str()
    support_type_1st = fields.Str()
    support_type_2nd = fields.Str()
    approver = fields.Str()
    support_start_date = fields.Str()
    support_end_date = fields.Str()
    published_date = fields.Str()
    record_content = fields.Str()
    account_name = fields.Str()
    project_name = fields.Str()
    record_data = fields.Str()
    project_owner_name = fields.Str()
    project_sales_by_name = fields.Str()
    project_opportunity_number = fields.Str()
    project_opportunity_name = fields.Str()
    project_subject = fields.Str()
    cc_reason = fields.Str()
    project_total_support_duration = fields.Str()
    project_customer_requirement = fields.Str()


class SeProjectRecordApprovedDICAPP(Template):
    __id__ = '6364'
    __media__ = 'wexin_work_app'

    task_name = fields.Str()
    account_name = fields.Str()
    support_type_1st = fields.Str()
    support_type_2nd = fields.Str()
    support_start_date = fields.Str()
    support_duration = fields.Str()
    record_creator = fields.Str()
    support_location = fields.Str()


class SeProjectRecordUnApprovedEmail(Template):
    __id__ = '6349'
    __media__ = 'email'
    task_id = fields.Str()
    task_number = fields.Str()
    subject = fields.Str()
    approver = fields.Str()
    site_domain = fields.Str()
    record_content = fields.Str()
    reject_reason = fields.Str()


class SeProjectRecordReturnEmail(Template):
    __id__ = '6362'
    __media__ = 'email'
    task_number = fields.Str()
    subject = fields.Str()
    site_domain = fields.Str()
    task_id = fields.Str()
    approver = fields.Str()
    record_content = fields.Str()


class SeProjectTaskArchiveEmail(Template):
    __id__ = '6350'
    __media__ = 'email'
    task_id = fields.Str()
    site_domain = fields.Str()
    task_number = fields.Str()
    subject = fields.Str()


class SeProjectProjectArchiveEmail(Template):
    __id__ = '6351'
    __media__ = 'email'
    project_number = fields.Str()
    subject = fields.Str()
    site_domain = fields.Str()
    project_id = fields.Str()


class SeProjectTaskApprovedEmail(Template):
    __id__ = '6352'
    __media__ = 'email'
    task_number = fields.Str()
    created_by_name = fields.Str()
    subject = fields.Str()
    site_domain = fields.Str()
    project_id = fields.Str()
    task_result = fields.Str()
    task_incomplete_reason = fields.Str()


class SeProjectTaskApprovedArchiveEmail(Template):
    __id__ = '6353'
    __media__ = 'email'
    task_number = fields.Str()
    subject = fields.Str()
    task_id = fields.Str()
    site_domain = fields.Str()


class SeProjectTaskUnApprovedArchiveEmail(Template):
    __id__ = '6354'
    __media__ = 'email'
    task_number = fields.Str()
    subject = fields.Str()
    task_id = fields.Str()
    site_domain = fields.Str()
    approver = fields.Str()
    reject_reason = fields.Str()


class SeWeeklyEmail(Template):
    __id__ = '6357'
    __media__ = 'email'
    subject = fields.Str()
    data = fields.Str()


class DicTicketEmail(Template):
    __id__ = '6358'
    __media__ = 'email'
    commit = fields.Str()
    number = fields.Str()
    status = fields.Str()
    subject = fields.Str()
    priority = fields.Str()
    support_type = fields.Str()

class DicTicketTaskEmail(Template):
    __id__ = '6359'
    __media__ = 'email'
    number = fields.Str()
    subject = fields.Str()
    priority = fields.Str()
    support_type = fields.Str()
    task_subject = fields.Str()
    task_support_type = fields.Str()
    assign_by_name = fields.Str()

class DicTicketMessageEmail(Template):
    __id__ = '6360'
    __media__ = 'email'
    commit = fields.Str()
    number = fields.Str()
    subject = fields.Str()
    content = fields.Str()


class CloudLabFailCreateEmail(Template):
    __id__ = '6367'
    __media__ = 'email'
    instance_id = fields.Str()
    instance_name = fields.Str()
    create_time = fields.Str()
    reason = fields.Str()
