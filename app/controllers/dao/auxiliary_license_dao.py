from datetime import datetime
import json
from app.models import db
from app.models.auxiliary_license import AuxiliaryApplyLicenseRecord
from app.models.techadmin import SysUser 
from sqlalchemy.orm import aliased
from sqlalchemy import and_


class AuxiliaryApplyLicenseRecordDao:

    @staticmethod
    def queryLicenseRecord(**kwargs) -> set: 
        page = kwargs.get("page", 1)
        size = kwargs.get("size", 15)
        create_user =  aliased(SysUser)
        query = db.session.query(create_user, AuxiliaryApplyLicenseRecord)
        query = query.outerjoin(create_user, AuxiliaryApplyLicenseRecord.created_by_id == create_user.id)
        query = query.filter(AuxiliaryApplyLicenseRecord.created_by_id==kwargs.get("user_id"))
        if "crm_order" in kwargs:
            crm_order = kwargs.get("crm_order")
            like_clause = f"%{crm_order}%"
            query = query.filter(AuxiliaryApplyLicenseRecord.id.ilike(like_clause))
        if "status" in kwargs:
            query = query.filter(AuxiliaryApplyLicenseRecord.status.in_(kwargs.get("status")))
        if "account_id" in kwargs:
            query = query.filter(AuxiliaryApplyLicenseRecord.account_id==kwargs.get("account_id"))
        if "sn" in kwargs:
            query = query.filter(AuxiliaryApplyLicenseRecord.sn==kwargs.get("sn"))
        if "product_name" in kwargs:
            product_name = kwargs.get("product_name")
            like_clause = f"%{product_name}%"
            query = query.filter(AuxiliaryApplyLicenseRecord.product_name.ilike(like_clause))
        if "lic_param" in kwargs:
            query = query.filter(AuxiliaryApplyLicenseRecord.lic_param.in_(kwargs.get("lic_param")))
        total = query.count()
        offset = (page - 1) * size
        query = query.order_by(AuxiliaryApplyLicenseRecord.created_date.desc()).offset(offset).limit(size)
        return page, size, total, query
    
    @staticmethod
    def addLicenseRecord(crm_order: str, account_id: str, sn: str, product_name: str, lic_params: list, created_by_id: str,
                         email: str, status: str, order_id: str,  end_time: str, object_name: str, error_msg: str):
        license_record = AuxiliaryApplyLicenseRecord(
            id = crm_order,
            account_id = account_id,
            sn = sn,
            product_name = product_name,
            lic_params = json.dumps(lic_params),
            created_by_id = created_by_id,
            email = email,
            status = status,
            order_id = order_id,
            object_name = object_name,
            error_msg = error_msg,
            end_time = datetime.strptime(end_time, "%Y-%m-%d"),
            created_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        db.session.add(license_record)
        db.session.commit()
    
    @staticmethod
    def queryAllLicenseRecordID() -> list:
        try:
            records = AuxiliaryApplyLicenseRecord.query.filter(AuxiliaryApplyLicenseRecord.id).all()
            id_list = [result.id for result in records]
            return id_list
        except Exception as error:
            return []

    @staticmethod
    def getLicenseRecordByOrderID(order_id: str):
        record = AuxiliaryApplyLicenseRecord.query.filter(AuxiliaryApplyLicenseRecord.order_id==order_id).first()
        return record