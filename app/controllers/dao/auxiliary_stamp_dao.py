from datetime import datetime
from app.models import db
from app.models.auxiliary_stamp import AuxiliaryStamp
from app.models.techadmin import SysUser 
from sqlalchemy.orm import aliased
from sqlalchemy import and_, or_
from app.extensions import logger

class AuxiliaryStampDao:

    @staticmethod
    def queryConditionRecord(**kwargs) -> set:
        page = kwargs.get("page", 1)
        size = kwargs.get("size", 15)
        user_id = kwargs.get("user_id")
        stamp_user, request_user =  aliased(SysUser), aliased(SysUser)
        query = db.session.query(request_user, stamp_user, AuxiliaryStamp)
        query = query.outerjoin(stamp_user, AuxiliaryStamp.stamp_by_id == stamp_user.id)
        query = query.outerjoin(request_user, AuxiliaryStamp.request_by_id == request_user.id)
        query = query.filter(or_(AuxiliaryStamp.request_by_id == user_id, AuxiliaryStamp.stamp_by_id == user_id))
        if "file_name" in kwargs:
            file_name = kwargs.get("file_name")
            like_clause = f"%{file_name}%"
            query = query.filter(AuxiliaryStamp.file_name.ilike(like_clause))
        if "status" in kwargs:
            query = query.filter(AuxiliaryStamp.status.in_(kwargs.get("status")))
        if "stamp_by_id" in kwargs:
            query = query.filter(AuxiliaryStamp.request_by_id==kwargs.get("stamp_by_id"))
        if "request_by_id" in kwargs:
            query = query.filter(AuxiliaryStamp.request_by_id==kwargs.get("request_by_id"))
        if "reason" in kwargs:
            reason = kwargs.get("reason")
            like_clause = f"%{reason}%"
            query = query.filter(AuxiliaryStamp.reason.ilike(like_clause))
        if "created_date" in kwargs:
            created_date = kwargs.get("created_date")
            query = query.filter(and_(AuxiliaryStamp.created_date >= created_date[0], AuxiliaryStamp.created_date <= created_date[1]))
        if "stamp_date" in kwargs:
            stamp_date = kwargs.get("stamp_date")
            query = query.filter(and_(AuxiliaryStamp.stamp_date >= stamp_date[0], AuxiliaryStamp.stamp_date <= stamp_date[1]))

        total = query.count()
        offset = (page - 1) * size
        query = query.order_by(AuxiliaryStamp.created_date.desc()).offset(offset).limit(size)

        return page, size, total, query
    
    @staticmethod
    def addStampRecord(file_name: str, request_by_id: str, reason: str, file_id: str, stamp_by_id: str, 
                       status: str, object_name: str):
        stamp_record = AuxiliaryStamp(
            file_name = file_name,
            request_by_id = request_by_id,
            reason = reason,
            file_id = file_id,
            stamp_by_id = stamp_by_id,
            status = status,
            object_name = object_name,
            created_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        db.session.add(stamp_record)
        db.session.commit()
        
    @staticmethod
    def updateStatusByFileId(file_id: str, update_data: int):
        try:
            AuxiliaryStamp.query.filter(AuxiliaryStamp.file_id==file_id).update(update_data)
            db.session.commit()
        except:
            logger.error(f"No record found for file_id: {file_id}")

    @staticmethod
    def getStampRecordByFileId(file_id: str):
        stamp_record = AuxiliaryStamp.query.filter(AuxiliaryStamp.file_id==file_id).first()
        return stamp_record