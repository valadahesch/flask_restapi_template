from . import db

from sqlalchemy import DateTime, String, Unicode
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER

t_GetLeadList = db.Table(
    'GetLeadList',
    db.Column('leadid', UNIQUEIDENTIFIER, nullable=False),
    db.Column('new_code', Unicode(100)),
    db.Column('owneridname', Unicode(160)),
    db.Column('new_state', Unicode(4000)),
    db.Column('new_transferred_customer', String(2, 'Chinese_PRC_90_CI_AI')),
    db.Column('new_transferred_lead', String(2, 'Chinese_PRC_90_CI_AI')),
    db.Column('opportunitycode', Unicode(100)),
    db.Column('new_opportunity', Unicode(300)),
    db.Column('opportunitystage', Unicode(4000)),
    db.Column('companyname', Unicode(100)),
    db.Column('fullname', Unicode(100)),
    db.Column('phone', Unicode(100)),
    db.Column('requiredescribe', Unicode(100)),
    db.Column('province', Unicode),
    db.Column('city', Unicode(4000)),
    db.Column('caseusernamae', Unicode(100)),
    db.Column('owneridbelongname', Unicode(160)),
    db.Column('accountname', Unicode(259)),
    db.Column('createdon', DateTime),
    db.Column('modifiedon', DateTime),
    info={'bind_key': 'crm_views'}
)

t_View_AssignablePerson = db.Table(
    'View_AssignablePerson',
    db.Column('ID', UNIQUEIDENTIFIER, nullable=False),
    db.Column('SE分派员Userid', UNIQUEIDENTIFIER),
    db.Column('SE分派员人力工号', Unicode(100)),
    db.Column('SE分派员邮箱地址', Unicode(100)),
    db.Column('SE分派员姓名', Unicode(256)),
    db.Column('可分派用户Userid', UNIQUEIDENTIFIER),
    db.Column('可分派用户人力工号', Unicode(100)),
    db.Column('可分派用户邮箱地址', Unicode(100)),
    db.Column('可分派用户姓名', Unicode(256))
)


t_VIEW_ACCOUNT = db.Table(
    'VIEW_ACCOUNT',
    db.Column('accountid', UNIQUEIDENTIFIER, nullable=False),
    db.Column('oldaccountid', Unicode(100)),
    db.Column('name', Unicode(259)),
    db.Column('onelevelindustry', Unicode(100)),
    db.Column('twolevelindustry', Unicode(100)),
    db.Column('ownerid', UNIQUEIDENTIFIER),
    db.Column('managerid', UNIQUEIDENTIFIER),
    db.Column('accountlogtype', String(200, 'Chinese_PRC_90_CI_AI')),
    db.Column('accountcode', Unicode(100)),
    db.Column('accounttype', String(200, 'Chinese_PRC_90_CI_AI')),
    db.Column('saleunitid', UNIQUEIDENTIFIER),
    db.Column('accountcompactness', String(200, 'Chinese_PRC_90_CI_AI')),
    db.Column('accountnumber', Unicode(100)),
    db.Column('area', Unicode(100)),
    db.Column('region', Unicode(100)),
    db.Column('country', Unicode(100)),
    db.Column('province', Unicode(100)),
    db.Column('city', Unicode(100)),
    db.Column('isvalidaccount', String(2, 'Chinese_PRC_90_CI_AI'), nullable=False),
    db.Column('approvalstatus', String(200, 'Chinese_PRC_90_CI_AI')),
    db.Column('phone', Unicode(500)),
    db.Column('accountservelevel', String(200, 'Chinese_PRC_90_CI_AI')),
    db.Column('industry3d', String(200, 'Chinese_PRC_90_CI_AI')),
    db.Column('createdon', DateTime),
    db.Column('ModifiedOn', DateTime),
    db.Column('ModifiedBy', UNIQUEIDENTIFIER),
    db.Column('state', String(200, 'Chinese_PRC_90_CI_AI')),
    db.Column('new_tycreturn', String(2, 'Chinese_PRC_90_CI_AI'), nullable=False),
    db.Column('new_managementstatus', Unicode(500))
)


t_VIEW_SE_PROJECT_OPPORTUNITY = db.Table(
    'VIEW_SE_PROJECT_OPPORTUNITY',
    db.Column('活动编号', Unicode(100)),
    db.Column('商机名称', Unicode(300)),
    db.Column('商机编号', Unicode(100)),
    db.Column('商机阶段', Unicode(100))
)