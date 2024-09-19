import re
import requests
from app.extensions import logger
from app.utils.api_util import AppException
from app.controllers.dao.dic_ticket_dao import DICTicketsDao, DICTicketTaskDao


class GitLab():

    def __init__(self, token: str="qyHPymGzC_xwpdseCByX"):
        self.headers = {"PRIVATE-TOKEN": token}
        self.base_url = "https://git.tac.hillstonenet.com/api/v4"

    def getIssueDetail(self, project_id: str, issue_id: str) -> dict:
        """
        function: 获取某个项目下,某个issue的详细信息;
        params: 
            - project_id: 项目ID,
            - issue_id:   issue ID
        """
        url = f"{self.base_url}/projects/{project_id}/issues/{issue_id}"
        response = requests.get(url=url, verify=False, headers=self.headers)
        if response.status_code  in [200, 201]:
            return response.json()
        else:
            error_message = f"获取项目ID:{project_id},issue_id:{issue_id}信息失败"
            logger.error(error_message)
            raise AppException(error_message)

    def setIssue(self, project_id: str, title: str, description: str, milestone_id: str):
        """
        function: 在某个项目下,新建一个issue;
        params: 
            - description:     项目ID
            - labels:          issue ID
            - milestone_id:    里程碑ID
        """
        url = f"{self.base_url}/projects/{project_id}/issues"
        post_data = {
            "id": project_id,
            "title": title,
            "description": description,
            "milestone_id": milestone_id
        }
        response = requests.post(url=url, verify=False, data=post_data, headers=self.headers)
        if response.status_code  in [200, 201]:
            return response.json()
        else:
            error_message = f"创建新issue失败, 项目ID:{project_id}"
            logger.error(error_message)
            raise AppException(error_message)


    def updateIssue(self, project_id: str, issue_id: str, title: str, description: str, labels: str, 
                    milestone_id: str, state_event: str) -> bool:
        """
        function: 更新某个项目下的某一个issue;
        params: 
            - state_event:    issue状态 close
        """
        url = f"{self.base_url}/projects/{project_id}/issues/{issue_id}"
        put_data = {
            "id": project_id,
            "title": title,
            "description": description,
            "labels": labels,
            "milestone_id": milestone_id,
            "state_event": state_event
        }
        response = requests.post(url=url, verify=False, data=put_data, headers=self.headers)
        if response.status_code  in [200, 201]:
            return response.json()
        else:
            error_message = f"更新新issue失败, 项目ID:{project_id}, issue_id:{issue_id}"
            logger.error(error_message)
            raise AppException(error_message)

    def getMilestone(self, project_id: str, milestone_id: str) -> dict:
        """
        function: 获取某个项目下的某一个里程碑详细信息;
        """
        url = f"{self.base_url}/projects/{project_id}/milestones/{milestone_id}"
        response = requests.get(url=url, verify=False, headers=self.headers)
        if response.status_code  in [200, 201]:
            return response.json()
        else:
            error_message = f"获取项目ID:{project_id},里程碑ID:{milestone_id}信息失败"
            logger.error(error_message)
            raise AppException(error_message)

    def getProjectInfo(self, project_id: str) -> dict:
        url = f"{self.base_url}/projects/{project_id}"
        response = requests.get(url=url, verify=False, headers=self.headers)
        if response.status_code  in [200, 201]:
            return response.json()
        else:
            error_message = f"获取项目ID:{project_id}信息失败"
            logger.error(error_message)
            raise AppException(error_message)
    
    def setMilestone(self, project_id: str, title: str, description: str, due_date: str="YYYY-MM-DD", 
                     start_date: str="YYYY-MM-DD"):
        """
        function: 在某个项目下, 新建一个里程碑;
        params:
            - due_date: 结束时间
            - start_date: 开始时间
        """
        url = f"{self.base_url}/projects/{project_id}/milestones"
        post_data = {
            "id": project_id,
            "title": title,
            "description": description,
            "due_date": due_date,
            "start_date": start_date
        }
        response = requests.post(url=url, verify=False, data=post_data, headers=self.headers)
        if response.status_code in [200, 201]:
            return response.json()
        else:
            error_message = f"创建新里程碑失败, 项目ID:{project_id},故障可能原因: 1. 开始时间不早于结束时间; 2. 主题可能重复"
            logger.error(error_message)
            raise AppException(error_message)

    def updateMilestone(self, project_id: str,  milestone_id: str, title: str, description: str, state_event: str,
                        due_date: str, start_date: str):
        """
        function: 更新在某个项目下的某一个里程碑;
        """
        url = f"{self.base_url}/projects/{project_id}/milestones/{milestone_id}"
        put_data = {
            "id": project_id,
            "title": title,
            "description": description,
            "due_date": due_date,
            "start_date": start_date,
            "state_event": state_event
        }
        response = requests.put(url=url, verify=False, data=put_data, headers=self.headers)
        if response.status_code  in [200, 201]:
            return response.json()
        else:
            error_message = f"更新里程碑失败, 项目ID:{project_id}, 里程碑ID: {milestone_id}"
            logger.error(error_message)
            raise AppException(error_message)
    
    def listProjectIssueDiscussion(self, project_id: str, issue_id: str) -> list:
        """
        function: 列出某个项目下某个issue下的留言全部信息;
        """
        url = f"{self.base_url}/projects/{project_id}/issues/{issue_id}/discussions"
        response = requests.get(url=url, verify=False, headers=self.headers)
        if response.status_code  in [200, 201]:
            return response.json()
        else:
            error_message = f"获取项目ID:{project_id},issue ID:{issue_id}留言信息失败"
            logger.error(error_message)
            raise AppException(error_message)
        
    def getMilestoneSchedule(self, milestone_id: str, project_id: str):
        try:
            url = f"{self.base_url}/projects/{project_id}/milestones/{milestone_id}/issues"
            response = requests.get(url, headers=self.headers)
            schedule = 0
            if response.status_code in [200, 201]:
                closed_issue = [issue for issue in response.json() if issue.get("state") == "closed"]
                schedule = len(closed_issue) / len(response.json())
                return "{:.2f}".format(schedule), schedule, response.json()
        except:
            logger.error(f"获取进度条数据失败,里程碑ID: {milestone_id}, 项目ID: {project_id}")
            return "{:.2f}".format(schedule), schedule, response.json()


class GitLabDICTicket(GitLab):

    def __init__(self, token: str="qyHPymGzC_xwpdseCByX"):
        super().__init__(token)

    def createTask(self, milestone_title: str, milestone_description: str, project_id: str,
                   start_time: str, end_time: str) -> dict:
        
        milestone = self.setMilestone(project_id, milestone_title, milestone_description, end_time, start_time)
        milestone_id = milestone.get("id")
        self.setIssue(project_id, milestone_title, milestone_description, milestone_id)
        return milestone_id
    
    def getTaskInfoById(self, ticket_id: str) -> dict:
        try:
            tasks = DICTicketTaskDao.getTaskByTicketId(ticket_id)
            for task in tasks["list"]:
                if task.get("handle_type") == "develop":
                    task_schedule, task_schedule_int, issues_data = self.getMilestoneSchedule(project_id=task.get("project_id"), milestone_id=task.get("milestone_id"))
                    milestone_data = issues_data[0]["milestone"]
                    result = re.search(r'[^/]+/[^/]+/([^/]+)/[^/]+', milestone_data.get("web_url"))
                    if result:
                        task["project_name"] = result.group(1)
                    else:
                        task["project_name"] = ""
                    task["milestone_url"] = milestone_data.get("web_url")
                    task["milestone_status"] = milestone_data.get("state")
                    task["milestone_title"] = milestone_data.get("title")
                    task["milestone_schedule"] = task_schedule
                    task["start_time"] = milestone_data.get("start_date")
                    task["end_time"] = milestone_data.get("due_date")
                    task["description"] = milestone_data.get("description")
                    task["issue"] = []
                    for issue in issues_data:
                        issue_data = {
                            "id": issue.get("id"),
                            "subject": issue.get("title"),
                            "status": issue.get("state"),
                            "label": issue.get("labels"),
                            "end_time": issue.get("due_date") or "",
                            "issue_url": issue.get("web_url")
                        }
                        task["issue"].append(issue_data)
            return tasks
        except:
            raise AppException(message="获取任务信息失败,请联系管理员")

    def getTicketSchedule(self, ticket_id: str) -> str:
        try:
            tasks = DICTicketTaskDao.getTaskByTicketId(ticket_id).get("list")
            ticket_schedule, count = 0, 0
            if tasks:
                for task in tasks:
                    count += 1
                    if task.get("handle_type") == "non_develop":
                        ticket_schedule += 1
                    else:
                        task_schedule, task_schedule_int, issues_data = self.getMilestoneSchedule(project_id=task.get("project_id"), milestone_id=task.get("milestone_id"))
                        ticket_schedule += task_schedule_int
                ticket_schedule = ticket_schedule / count
            return "{:.2f}".format(ticket_schedule)
        except:
            ticket_schedule = 0.00
            logger.error(f"获取工单:{ticket_id}进度失败")
        finally:
            return "{:.2f}".format(ticket_schedule)