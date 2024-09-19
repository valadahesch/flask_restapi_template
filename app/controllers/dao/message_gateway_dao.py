from app.models.message_gateway import MessageTemplate  
from app.models import db
from app.utils.api_util import AppException
from app.models.techadmin import SysUser
from sqlalchemy import or_, and_, not_
from sqlalchemy.orm import joinedload, outerjoin, aliased


class MessageGatewayTempalteDao():

    @staticmethod
    def queryMessageTemplateById(template_id: str) -> dict:
        created_user, edit_user =  aliased(SysUser), aliased(SysUser)
        query = db.session.query(MessageTemplate, created_user, edit_user)
        query = query.outerjoin(created_user, MessageTemplate.created_by_id == created_user.id)
        query = query.outerjoin(edit_user, MessageTemplate.last_modified_by_id == edit_user.id)
        query = query.filter(MessageTemplate.id == template_id)
        for template, created_user, edit_user in query.all():
            if not template:
                raise AppException("查询失败,消息网关模版不存在")
            template_data = {
                "id": template.id,
                "template_number": template.template_number,
                "subject": template.subject, 
                "content": template.content,
                "created_by_id": template.created_by_id, 
                "created_by_name": created_user.display_name, 
                "created_date": str(template.created_date), 
                "last_modified_by_id": template.last_modified_by_id, 
                "last_modified_by_name": edit_user.display_name,
                "last_modified_date": str(template.last_modified_date),
                "enable": template.enable, 
                "media_type": template.media_type,
                "language": template.language,
                "remark": template.remark
            }
        return template_data
    
    @staticmethod
    def queryMessageTemplateList(query_data: dict) -> list[MessageTemplate]:

        page = query_data.get("page", 1)
        size = query_data.get("size", 15)
        language, enable = query_data.get("language"), query_data.get("enable") 
        media_type, like, template_data = query_data.get("media_type"), query_data.get("like"), []
        
        created_user, edit_user =  aliased(SysUser), aliased(SysUser)
        query = db.session.query(MessageTemplate, created_user, edit_user)
        query = query.outerjoin(created_user, MessageTemplate.created_by_id == created_user.id)
        query = query.outerjoin(edit_user, MessageTemplate.last_modified_by_id == edit_user.id)

        if enable:
            print(enable)
            query = query.filter(MessageTemplate.enable.in_(enable))
        if language:
            query = query.filter(MessageTemplate.language.in_(language))
        if media_type:
            query = query.filter(MessageTemplate.media_type.in_(media_type))
        if like:
                like_clause = f"%{like}%"
                query = query.filter(or_(MessageTemplate.subject.ilike(like_clause), 
                                         MessageTemplate.content.ilike(like_clause),
                                         MessageTemplate.remark.ilike(like_clause),
                                         MessageTemplate.template_number.ilike(like_clause)))
        total = query.count()
        offset = (page - 1) * size
        query = query.order_by(MessageTemplate.created_date.desc()).offset(offset).limit(size)

        for template, created_user, edit_user in query.all():
            data = {
                "id": template.id,
                "template_number": template.template_number,
                "subject": template.subject, 
                "content": template.content,
                "created_by_id": template.created_by_id, 
                "created_by_name": created_user.display_name, 
                "created_date": str(template.created_date), 
                "last_modified_by_id": template.last_modified_by_id, 
                "last_modified_by_name": edit_user.display_name,
                "last_modified_date": str(template.last_modified_date),
                "enable": template.enable, 
                "media_type": template.media_type,
                "language": template.language,
                "remark": template.remark
            }
            template_data.append(data)
        return {"page": page, "size": size, "total": total, "list": template_data}

    @staticmethod
    def updateMessageTemplateById(_id: str, update_data: dict) -> bool:
        MessageTemplate.query.filter(MessageTemplate.id == _id).update(update_data)
        db.session.commit()
        return True

    @staticmethod
    def addMessageTemplate(data: dict) -> bool:
        try:
            template = MessageTemplate(data)
            db.session.add(template)
            db.session.commit()
            return True
        except Exception as error:
            db.session.rollback()
            raise AppException(message=error)


    @staticmethod
    def queryAllTemplateId() -> list:
        templates = MessageTemplate.query.with_entities(MessageTemplate.id).all()
        templates_id = [template.id for template in templates] if templates else []
        return templates_id