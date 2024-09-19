from app.models import db
from datetime import datetime
from sqlalchemy import or_
from app.models.file_system import SysFileManage
from app.models.techadmin import SysUser
from sqlalchemy.orm import aliased

class SysFileManageDao:

    @staticmethod
    def uniqueId(_id) -> bool:
        app_db = db.get_app()
        with app_db.app_context():
            res = SysFileManage.query.filter(SysFileManage.id == id).first()

        if res:
            return True
        return False

    @staticmethod
    def addDirectory(new_directory: SysFileManage) -> str:
        new_directory.created_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db.session.add(new_directory)
        db.session.commit()
        return new_directory.id
    
    @staticmethod
    def queryRootDirectoryByRelatedObjectId(related_object_id: str) -> SysFileManage:
        res = SysFileManage.query.filter(SysFileManage.obj_type == "root_dir", 
                                         SysFileManage.related_object_id == related_object_id,
                                         or_(SysFileManage.deleted_by_id.is_(None), 
                                         SysFileManage.deleted_by_id == "")).first()
        return res
    
    @staticmethod
    def queryDirectoryByRelatedObject(related_object_type, related_object_id) -> SysFileManage:
        res = SysFileManage.query.filter(SysFileManage.related_object_type == related_object_type, 
                                         SysFileManage.related_object_id == related_object_id,
                                         or_(SysFileManage.deleted_by_id.is_(None), 
                                         SysFileManage.deleted_by_id == "")).first()
        return res
    
    @staticmethod
    def querySubByFolderId(folder_id: str) -> list:
        query = db.session.query(SysFileManage, SysUser)
        query = query.outerjoin(SysUser, SysFileManage.created_by_id == SysUser.id)
        query = query.order_by(SysFileManage.created_date.desc())
        res = query.filter(SysFileManage.parent_id == folder_id).all()
        return res

    @staticmethod
    def queryFolderByFileName(folder_id, file_name) -> bool:
        res = SysFileManage.query.filter(SysFileManage.parent_id == folder_id, 
                                         SysFileManage.obj_name == file_name,
                                         or_(SysFileManage.deleted_by_id.is_(None), 
                                         SysFileManage.deleted_by_id == "")).first()
        return res
        
    @staticmethod
    def queryFolderByIdIsExist(_id: str) -> bool:
        res = SysFileManage.query.filter(SysFileManage.id == _id).first()
        if res:
            return True
        else:
            return False
        
    @staticmethod
    def queryFolderById(_id: str) -> SysFileManage:
        res = SysFileManage.query.filter(SysFileManage.id == _id).first()
        return res

    @staticmethod
    def queryFolderByIdOutJoinSysUser(_id: str) -> SysFileManage:
        query = db.session.query(SysFileManage, SysUser)
        query = query.outerjoin(SysUser, SysFileManage.created_by_id == SysUser.id)
        res = query.filter(SysFileManage.id == _id).first()
        return res
        
    @staticmethod
    def deleteFolderByid(file_id: str, delete_by_id: str):
        now_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        delete_data = {}
        delete_data["deleted_date"] = now_datetime
        delete_data["deleted_by_id"] = delete_by_id
        SysFileManage.query.filter(SysFileManage.id == file_id).update(delete_data)
        db.session.commit()


    @staticmethod
    def updataFolderByid(file_id: str, update_data: dict):
        SysFileManage.query.filter(SysFileManage.id == file_id).update(update_data)
        db.session.commit()

    @staticmethod
    def getAllChildren(parent_id) -> list:
        child = aliased(SysFileManage)
        recursive_query = (
            db.session.query(child)
            .filter(child.parent_id == parent_id)
            .cte(name="recursive", recursive=True)
        )

        recursive_query = recursive_query.union_all(
            db.session.query(child).join(recursive_query, child.parent_id == recursive_query.c.id)
        )
        result = db.session.query(recursive_query).all()
        children_ids = []
        for i in result:
            children_ids.append(i.id)
        return children_ids