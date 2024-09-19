from app.models.dic_ticket import DICTicketTask, DICTickets, DICTicketMessage, DICTicketProject, \
                                  DICTicketFunctionalModule
from app.models import db
from app.models.techadmin import SysMenu, SysRoleMenu, SysRoleUser, SysUser, TblEmployee
from sqlalchemy import or_, and_, not_
from sqlalchemy.orm import joinedload, outerjoin, aliased
from app.utils.api_util import AppException
from app.utils.func_util import getCurrentTime, getRandomString20

class SysUserDepartmet:
    
    @staticmethod
    def isAdmin(user_id: str) -> bool:
        try:
            role_users = SysRoleUser.query.filter(SysRoleUser.user_id == user_id).all()
            role_ids = [role_user.role_id for role_user in role_users]
            role_menu_list = db.session.query(SysRoleMenu).join(
                SysMenu, SysRoleMenu.menu_id == SysMenu.id).filter(
                SysMenu.permission == "dic_ticket_manage:all", SysRoleMenu.role_id.in_(role_ids)
            ).all()
            if role_menu_list:
                admin = True
            else:
                admin = False
        except:
            admin = False
        finally:
            return admin 

    @staticmethod
    def getUsernameById(user_id: str) -> str:
        user = SysUser.query.filter(SysUser.id == user_id).first()
        return user.display_name
    
    @staticmethod
    def getEmailById(user_id: str) -> str:
        user = SysUser.query.filter(SysUser.id == user_id).first()
        return user.email

    @staticmethod
    def getEmailAndDisplaynameById(user_id: str) -> set:
        try:
            user = SysUser.query.filter(SysUser.id == user_id).first()
            return user.email, user.display_name
        except:
            raise AppException(message="获取用户信息失败")

class DICTicketsDao:

    @staticmethod
    def queryTicketParticipant(ticket_id: str) -> list:
        try:
            created_user, commit_user =  aliased(SysUser), aliased(SysUser)
            message_user, assign_user =  aliased(SysUser), aliased(SysUser)
            query = db.session.query(DICTickets, DICTicketMessage, DICTicketTask, created_user, commit_user,message_user, assign_user)
            query = query.outerjoin(DICTicketMessage, DICTickets.id == DICTicketMessage.ticket_id)
            query = query.outerjoin(DICTicketTask, DICTickets.id == DICTicketTask.ticket_id)
            query = query.outerjoin(created_user, DICTickets.commit_by_id == created_user.id)
            query = query.outerjoin(commit_user, DICTickets.created_by_id == commit_user.id)
            query = query.outerjoin(message_user, DICTicketMessage.created_by_id == message_user.id)
            query = query.outerjoin(assign_user, DICTicketTask.assign_by_id == assign_user.id)
            query = query.filter(DICTickets.id == ticket_id)
            query = query.filter(DICTicketMessage.created_by_id != "0")
            participants = []
            for ticket, message, task, created_user, commit_user, message_user, assign_user in query.all():
                if created_user:
                    participants += [created_user.email]
                if commit_user:
                    participants += [commit_user.email]
                if message_user:
                    participants += [message_user.email]
                if assign_user:
                    participants += [assign_user.email]
            return participants
        except:
            raise AppException("获取工单参与人信息失败")


    @staticmethod
    def queryeTicketIsExist(ticket_id: str) -> bool:
        ticket = DICTickets.query.filter(DICTickets.id == ticket_id).first()
        if ticket.status != "Deleted":
            return True
        else:
            return False

    @staticmethod
    def deleteTicket(ticket_id: str) -> bool:
        ticket = DICTickets.query.filter(DICTickets.id == ticket_id).first()
        if ticket:
            db.session.delete(ticket)
            db.session.commit()
            return True
        else:
            return False

    @staticmethod
    def updateTicket(**kwargs) -> bool:
        if "ticket_id" not in kwargs:
            raise AppException(message="未获取到工单ID")
        else:
            update_data = kwargs.get("update_data")
            ticket = DICTickets.query.filter(DICTickets.id == kwargs.get("ticket_id")).first()
            if update_data.get("parent_id"):
                ticket.parent_id=update_data.get("parent_id")
            if update_data.get("status"):
                ticket.status=update_data.get("status")
            if update_data.get("subject"):
                ticket.subject=update_data.get("subject")
            if update_data.get("description"):
                ticket.description=update_data.get("description")
            if update_data.get("support_type"):
                ticket.support_type = update_data.get("support_type")
            if update_data.get("privacy"):
                ticket.privacy = update_data.get("privacy")
            if update_data.get("functional_module_id"):
                ticket.functional_module_id = update_data.get("functional_module_id")
            if update_data.get("priority"):
                ticket.priority = update_data.get("priority")
            if update_data.get("feasibility"):
                ticket.feasibility=update_data.get("feasibility")
            if update_data.get("cancel_by_reason"):
                ticket.cancel_by_reason=update_data.get("cancel_by_reason")
            if update_data.get("cancel_by_id"):
                ticket.cancel_by_id=update_data.get("cancel_by_id")
            if update_data.get("cancel_date"):
                ticket.cancel_date=update_data.get("cancel_date")
            if update_data.get("last_modified_by_id"):
                ticket.last_modified_by_id=update_data.get("last_modified_by_id")
            if update_data.get("due_time"):
                ticket.due_time=update_data.get("due_time")
            if update_data.get("created_by_id"):
                ticket.created_by_id=update_data.get("created_by_id")
            if update_data.get("first_delivery_date"):
                ticket.first_delivery_date=update_data.get("first_delivery_date")
            if update_data.get("accepted_datetime"):
                ticket.accepted_datetime=update_data.get("accepted_datetime")
            if update_data.get("accepted_by_id"):
                ticket.accepted_by_id=update_data.get("accepted_by_id")
            if update_data.get("complete_date"):
                ticket.complete_date=update_data.get("complete_date")
            if update_data.get("actual_due_time"):
                ticket.actual_due_time=update_data.get("actual_due_time")
            ticket.last_modified_date = getCurrentTime()
            db.session.commit()
        return True

    @staticmethod
    def getTicketStatus(ticket_id: str) -> str:
        ticket = DICTickets.query.filter(DICTickets.id == ticket_id).first()
        return ticket.status

    @staticmethod
    def updateTicketStatus(ticket_id: str, status: str) -> bool:
        ticket = DICTickets.query.filter(DICTickets.id == ticket_id).first()
        ticket.status = status
        db.session.commit()
        return True

    @staticmethod
    def queryAllTicketIds():
        tickets = DICTickets.query.with_entities(DICTickets.id, DICTickets.number).all()
        if tickets:
            ticket_ids, number_ids = zip(*[(ticket.id, ticket.number) for ticket in tickets])
        else: 
            ticket_ids, number_ids = [], []
        return ticket_ids, number_ids
    
    @staticmethod
    def createTickets(ticket_data: dict) -> bool:
        ticket = DICTickets(
            id = ticket_data.get("id"),
            number = ticket_data.get("number"),
            parent_id = ticket_data.get("parent_id"),
            subject = ticket_data.get("subject"),
            description = ticket_data.get("description"),
            support_type = ticket_data.get("support_type"),
            privacy = ticket_data.get("privacy"),
            functional_module_id = ticket_data.get("functional_module_id"),
            priority = ticket_data.get("priority"),
            commit_by_id = ticket_data.get("commit_by_id"),
            created_by_id = ticket_data.get("created_by_id"),
            created_date = ticket_data.get("created_date"),
            status = ticket_data.get("action"),
            last_modified_by_id = ticket_data.get("last_modified_by_id"),
            last_modified_date = ticket_data.get("last_modified_date")
        )
        db.session.add(ticket)
        db.session.commit()
        return True
    
    @staticmethod 
    def queryDraftTickets(user_id: str, classification: str,  page: int, size: int, support_type: list, priority: list, 
                          privacy: list, like: str):
        page = page if page else 1
        size = size if size else 15
        created_user =  aliased(SysUser)
        query = db.session.query(DICTickets, DICTicketFunctionalModule, SysUser, created_user)
        query = query.outerjoin(DICTicketFunctionalModule, DICTickets.functional_module_id == DICTicketFunctionalModule.id)
        query = query.outerjoin(SysUser, DICTickets.commit_by_id == SysUser.id)
        query = query.outerjoin(created_user, DICTickets.created_by_id == created_user.id)
        query = query.filter(DICTickets.commit_by_id == user_id)
        query = query.filter(DICTickets.status == classification)
        if support_type:
            query = query.filter(DICTickets.support_type.in_(support_type))
        if priority:
            query = query.filter(DICTickets.priority.in_(priority))
        if privacy:
            query = query.filter(DICTickets.privacy.in_(privacy))
        if like:
                like_clause = f"%{like}%"
                query = query.filter(or_(DICTickets.number.ilike(like_clause), DICTickets.subject.ilike(like_clause)))
        total = query.count()
        offset = (page - 1) * size
        query = query.order_by(DICTickets.created_date.desc()).offset(offset).limit(size)
        tickets_objects, ticket_list = query.all(), []

        for ticket_object, functional_module, user, created_by in tickets_objects:
            ticket = {
                "id": ticket_object.id,
                "parent_id": ticket_object.parent_id,
                "number": ticket_object.number,
                "schedule": "0.00",
                "subject": ticket_object.subject,
                "status": ticket_object.status,
                "privacy": ticket_object.privacy,
                "commit_by_id": ticket_object.commit_by_id,
                "commit_by_name": user.display_name if user else "",
                "created_by_id": ticket_object.created_by_id,
                "created_by_name": created_by.display_name if created_by else "",
                "created_date": str(ticket_object.created_date),
                "last_modified_by_id": ticket_object.last_modified_by_id,
                "last_modified_date": str(ticket_object.last_modified_date),
                "support_type": ticket_object.support_type,
                "priority": ticket_object.priority,
                "functional_module_id": ticket_object.functional_module_id,
                "functional_module_name": functional_module.name if functional_module else "" 
            }
            ticket_list.append(ticket)
        return {"list": ticket_list, "page": page, "size": size, "total": total}
    
    @staticmethod 
    def queryTickets(classification: str, status: list, page: int, size: int, support_type: list, 
                     priority: list, user_id: str, admin: bool, privacy: list, like: str):
        page = page if page else 1
        size = size if size else 15
        created_user =  aliased(SysUser)
        query = db.session.query(DICTickets, DICTicketFunctionalModule, SysUser, created_user)
        query = query.outerjoin(DICTicketFunctionalModule, DICTickets.functional_module_id == DICTicketFunctionalModule.id)
        query = query.outerjoin(SysUser, DICTickets.commit_by_id == SysUser.id)
        query = query.outerjoin(created_user, DICTickets.created_by_id == created_user.id)
        if not admin:
            query = query.filter(
                or_(
                    DICTickets.privacy == "public",
                    and_(DICTickets.privacy == "private", DICTickets.created_by_id == user_id)
                )
            ) 
        if classification == 'mine':
            query = query.filter(or_(DICTickets.commit_by_id == user_id, DICTickets.created_by_id == user_id))
        if not status:
            query = query.filter(not_(DICTickets.status.in_(["Draft", "Deleted"])))    
        if status:
            query = query.filter(DICTickets.status.in_(status))
        if support_type:
            query = query.filter(DICTickets.support_type.in_(support_type))
        if priority:
            query = query.filter(DICTickets.priority.in_(priority))
        if privacy:
            query = query.filter(DICTickets.privacy.in_(privacy))
        if like:
                like_clause = f"%{like}%"
                query = query.filter(or_(DICTickets.number.ilike(like_clause), DICTickets.subject.ilike(like_clause)))
        total = query.count()
        offset = (page - 1) * size

        query = query.order_by(DICTickets.created_date.desc()).offset(offset).limit(size)
        tickets_objects, ticket_list = query.all(), []

        for ticket_object, functional_module, user, created_by in tickets_objects:
            ticket = {
                "id": ticket_object.id,
                "parent_id": ticket_object.parent_id,
                "number": ticket_object.number,
                "subject": ticket_object.subject,
                "status": ticket_object.status,
                "privacy": ticket_object.privacy,
                "commit_by_id": ticket_object.commit_by_id,
                "commit_by_name": user.display_name if user else "",
                "created_by_id": ticket_object.created_by_id,
                "created_by_name": created_by.display_name if created_by else "",
                "created_date": str(ticket_object.created_date),
                "last_modified_by_id": ticket_object.last_modified_by_id,
                "last_modified_date": str(ticket_object.last_modified_date),
                "support_type": ticket_object.support_type,
                "priority": ticket_object.priority,
                "functional_module_id": ticket_object.functional_module_id,
                "functional_module_name": functional_module.name if functional_module else ""
            }
            ticket_list.append(ticket)
        return {"list": ticket_list, "page": page, "size": size, "total": total}

    @staticmethod
    def getTicketAndFunctionalModule(ticket_id: str) -> dict:
        created_by = aliased(SysUser)
        query = db.session.query(DICTickets, DICTicketFunctionalModule, SysUser, created_by)
        query = query.outerjoin(DICTicketFunctionalModule, DICTickets.functional_module_id == DICTicketFunctionalModule.id)
        query = query.outerjoin(SysUser, DICTickets.created_by_id == SysUser.id)
        query = query.outerjoin(created_by, DICTickets.commit_by_id == created_by.id)
        query = query.filter(DICTickets.id == ticket_id)
        for ticket, functional_module, created_by, commit_by in query.all():
            data = {
                "id": ticket.id,
                "parent_id": ticket.parent_id,
                "number": ticket.number,
                "subject": ticket.subject,
                "description": ticket.description,
                "status": ticket.status,
                "commit_by_id": ticket.commit_by_id,
                "commit_by_name": commit_by.display_name if created_by else "",
                "created_by_id": ticket.created_by_id,
                "created_by_name": created_by.display_name if created_by else "",
                "created_date": str(ticket.created_date),
                "last_modified_by_id": ticket.last_modified_by_id,
                "last_modified_date": str(ticket.last_modified_date),
                "support_type": ticket.support_type,
                "priority": ticket.priority,
                "privacy": ticket.privacy,
                "feasibility": ticket.feasibility or "",
                "cancel_by_reason": ticket.cancel_by_reason or "",
                "functional_module_id": ticket.functional_module_id,
                "functional_module_name": functional_module.name if functional_module else ""
            }
        if ticket.first_delivery_date:
            data["first_delivery_date"] = str(ticket.first_delivery_date)
        if ticket.due_time:
            data["due_time"] = str(ticket.due_time)
        return data
    
    @staticmethod
    def getTicketById(ticket_id: str) -> dict:
        ticket = db.session.query(DICTickets).filter(DICTickets.id == ticket_id).first()
        data = {
            "id": ticket.id,
            "parent_id": ticket.parent_id,
            "number": ticket.number,
            "subject": ticket.subject,
            "description": ticket.description,
            "status": ticket.status,
            "commit_by_id": ticket.commit_by_id,
            "created_by_id": ticket.created_by_id,
            "commit_date": str(ticket.created_date),
            "last_modified_by_id": ticket.last_modified_by_id,
            "last_modified_date": str(ticket.last_modified_date),
            "support_type": ticket.support_type,
            "priority": ticket.priority,
            "functional_module_id": ticket.functional_module_id,
            "privacy": ticket.privacy,
            "due_time": str(ticket.due_time),
            "first_delivery_date": str(ticket.first_delivery_date),
            "accepted_by_id": ticket.accepted_by_id if ticket.accepted_by_id else ""
        }
        return data

class DICTicketTaskDao:

    @staticmethod
    def getTaskByUserId(user_id: str, page: int, size: int, ticket_status: str, task_subject: str, 
                        ticket_like: str) -> dict:
        page = page if page else 1
        size = size if size else 15

        created_user, assign_user =  aliased(SysUser), aliased(SysUser)
        query = db.session.query(DICTicketTask, DICTickets, DICTicketFunctionalModule, created_user, assign_user)
        query = query.outerjoin(created_user, DICTicketTask.created_by_id == created_user.id)
        query = query.outerjoin(assign_user, DICTicketTask.assign_by_id == assign_user.id)
        query = query.outerjoin(DICTickets, DICTicketTask.ticket_id == DICTickets.id)
        query = query.outerjoin(DICTicketFunctionalModule, DICTickets.functional_module_id == DICTicketFunctionalModule.id)
        query = query.filter(DICTicketTask.assign_by_id==user_id)
        if ticket_status:
            query = query.filter(DICTickets.status.in_(ticket_status))
        if ticket_like:
                like_clause = f"%{ticket_like}%"
                query = query.filter(or_(DICTickets.number.ilike(like_clause), DICTickets.subject.ilike(like_clause)))
        if task_subject:
                like_clause = f"%{task_subject}%"
                query = query.filter(DICTicketTask.subject.ilike(like_clause))
        total = query.count()
        offset = (page - 1) * size
        query = query.order_by(DICTicketTask.created_date.desc()).offset(offset).limit(size)
        tasks_data = []
        for task, ticket, functional_module, created_user, assign_user in query.all():
            data = {
                "id": task.id,
                "subject": task.subject,
                "created_by_name": created_user.display_name,
    			"created_by_id":  task.created_by_id,
      			"created_date": str(task.created_date),
                "assign_by_id": task.assign_by_id,
                "assign_by_name": assign_user.display_name,
                "handle_type": task.handle_type,
                "ticket_id": task.ticket_id,
                "ticket_subject": ticket.subject,
                "ticket_status": ticket.status,
                "ticket_number": ticket.number,
                "ticket_support_type": ticket.support_type,
    			"ticket_priority": ticket.priority,
                "functional_module_id": ticket.functional_module_id,
                "functional_module_name": functional_module.name if functional_module else ""
            }
            tasks_data.append(data)
        return {"page": page, "size": size, "total": total, "list": tasks_data}

    @staticmethod
    def queryAllTaskIds() -> list:
        tasks = DICTicketTask.query.with_entities(DICTicketTask.id).all()
        if tasks:
            task_ids = [task.id for task in tasks]
        else:
            task_ids = []
        return task_ids
    
    @staticmethod
    def createTask(id: str, ticket_id: str, handle_type: str, project_id: str, assign_by_id: str,
                    milestone_id: str, created_by_id: str, created_date: str, subject: str, description: str = ""):
        task = DICTicketTask(
            id=id,
            ticket_id=ticket_id,
            handle_type=handle_type,
            project_id=project_id,
            assign_by_id=assign_by_id,
            assign_date=created_date,
            milestone_id=milestone_id,
            created_by_id=created_by_id,
            created_date=created_date,
            subject=subject,
            description=description
        )
        db.session.add(task)
        db.session.commit()
        return True

    @staticmethod
    def getTaskByTicketId(ticket_id: str) -> set:
        query = db.session.query(DICTicketTask, SysUser)
        query = query.outerjoin(SysUser, DICTicketTask.assign_by_id == SysUser.id)
        query = query.filter(DICTicketTask.ticket_id == ticket_id)
        tasks_list, count = [], 0
        for task, user in query.all():
            task_data = {
                "task_id": task.id,
                "handle_type": task.handle_type,
                "milestone_id":  task.milestone_id,
                "project_id":  task.project_id,
                "project_id":  task.project_id,
                "assign_by_id":  task.assign_by_id,
                "description": task.description,
                "subject": task.subject,
                "assign_by_name":  user.display_name if user else "",
            }
            tasks_list.append(task_data)
            count = count + 1
        return {"list": tasks_list, "page": 1, "size": 100, "total": count}


class DICTicketProjectDao:

    @staticmethod
    def queryAllProject() -> dict:
        projects = DICTicketProject.query.filter(DICTicketProject.is_active == True).all()
        project_list = []
        for project in projects:
            data = {
                "id": project.id,
                "key": project.key,
                "project_name": project.project_name,
                "project_path": project.project_path,
                "created_by_id": project.created_by_id,
                "created_date": project.created_date.strftime('%Y-%m-%d %H:%M:%S')
            }
            project_list.append(data)
        return {"list": project_list}


class DICTicketMessageDao:

    @staticmethod
    def systemMessage(ticket_id: str, content: str):
        message_id = getRandomString20()
        all_message_id = DICTicketMessageDao.queryAllMessageID()
        while message_id in all_message_id:
            message_id = getRandomString20()
        DICTicketMessageDao.createMessage(message_id, '', ticket_id, content, False, '0', getCurrentTime(), 'system', '', '')
        return True

    @staticmethod
    def updateMessageNeedReply(message_id: str, need_reply: bool) -> bool:
        message = DICTicketMessage.query.filter(DICTicketMessage.id == message_id).first()
        message.need_reply = need_reply
        db.session.commit()
        return True
    
    @staticmethod
    def createMessage(message_id: str, parent_id: str, ticket_id: str, content: str, need_reply: bool, created_by_id: str, 
                      created_date: str, created_username: str, to_user_id: str, to_username: str) -> bool:
        message = DICTicketMessage(
            id=message_id,
            parent_id=parent_id,
            ticket_id=ticket_id,
            content=content,
            created_by_id=created_by_id,
            created_date=created_date,
            created_username=created_username,
            need_reply=need_reply,
            to_user_id=to_user_id,
            to_username=to_username
        )
        db.session.add(message)
        db.session.commit()
        return True

    @staticmethod
    def queryAllMessageID() -> list:
        messages = DICTicketMessage.query.with_entities(DICTicketMessage.id).all()
        if messages:
            messages_id = [message.id for message in messages]
        else:
            messages_id = []
        return messages_id
    
    @staticmethod
    def getMessageByTicketId(ticket_id: str, page: int, size: int) -> dict:
        messages_list = []
        query = DICTicketMessage.query.filter(DICTicketMessage.ticket_id == ticket_id)
        total = query.count()
        offset = (page - 1) * size
        query = query.order_by(DICTicketMessage.created_date.asc()).offset(offset).limit(size)
        for message in query.all():
            data = {
                "id": message.id,
                "created_by_id": message.created_by_id,
                "created_username": message.created_username,
                "to_user_id": message.to_user_id,
                "to_username": message.to_username,
                "parent_id": message.parent_id,
                "content": message.content,
                "need_reply": message.need_reply,
                "created_date": str(message.created_date)
            }
            messages_list.append(data)
        return {"list": messages_list, "page": page, "size": size, "total": total}

class DICTicketFunctionalModuleDao:
    
    @staticmethod
    def queryFunctionalModule() -> dict:
        functional_modules = DICTicketFunctionalModule.query \
            .filter(DICTicketFunctionalModule.is_active == True) \
            .order_by(DICTicketFunctionalModule.name.asc()) \
            .all()
        functional_module_list = []
        for functional_module in functional_modules:
            data = {
                "id": functional_module.id,
                "name": functional_module.name,
                "description": functional_module.description
            }
            functional_module_list.append(data)
        return {"list": functional_module_list}
