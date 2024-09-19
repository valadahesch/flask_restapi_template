# TechAdmin-Server
基于Python的Flask框架实现后台管理系统  
[![pipeline status](https://git.tac.hillstonenet.com/devops/techadmin-sever/badges/master/pipeline.svg)](https://git.tac.hillstonenet.com/devops/techadmin-sever/-/commits/master) [![coverage report](https://git.tac.hillstonenet.com/devops/techadmin-sever/badges/develop/coverage.svg)](https://git.tac.hillstonenet.com/devops/techadmin-sever/-/commits/develop)

* [系统管理](doc/system.md)  
* [呼叫中心](doc/call_center.md)  
* [商机线索](doc/business.md)  
* [SE内部事务](doc/se_work.md)
* [SE生态渠道](doc/se_eco_partner.md)
* [资源管理](doc/sys_resource.md)
* [云实验室](doc/cloud_lab.md)
* [SE项目管理](doc/se_project.md)
* 
其他： [开发规范](doc/standard.md)、 [枚举](app/enums)、 [权限列表](#权限列表)

 
## 发布流程
bugfix/issue<id> -> master  
feature/feature1 -> develop -> master  
hotfix -> master  
编译环境/编译依赖/编译项目->单元测试/推送镜像->开发/生产部署

## 项目部署
使用gitlab CI + Docker方式自动构建:  
环境安装：[安装GitLab Runner](https://docs.gitlab.com/runner/install/) ， 安装Docker  
配置文件： [.gitlab-ci.yml](.gitlab-ci.yml)，[Dockerfile](Dockerfile)，[run.sh](run.sh)  

Docker常用命令： 
```text
编译镜像：docker build --target project --no-cache -t techadmin-server .
启动服务： docker run -d -p 8000:8000 -e APP_ENV=dev --name techadmin-server techadmin-server  
列出所有容器： docker ps -a  
查看日志： docker logs -f <容器Id>  
进入容器： docker exec -it <容器Id> bash  
导出容器内日志： docker cp <容器Id>:/techadmin/logs ./  
清除不使用的镜像： docker image prune  
镜像打Tag: docker tag <镜像ID> <私有仓库地址>/python/techadmin:latest
登陆仓库： docker login <私有仓库地址> -u admin -p <密码>
推送私有仓库： docker push <私有仓库地址>/python/techadmin:latest
```

### 测试环境
服务器地址： 10.86.248.49  
Tag： sanbox

### 生产环境
服务器地址： 172.18.0.15  
Tag： prod_inspur


##  权限列表

`auxiliary.sn_query:all`
* POST [/api/auxiliary/sn/extract](app/views/auxiliary_platform/sn_api.py#L19)
* GET [/api/auxiliary/sn/query](app/views/auxiliary_platform/sn_api.py#L47)
  

`dic_ticket_manage:all`
* GET [/api/dic/ticket/functional_module/list](app/views/business_platform/dic_ticket_api.py#L76)
* POST [/api/dic/ticket](app/views/business_platform/dic_ticket_api.py#L88)
* DELETE [/api/dic/ticket/<string:ticket_id>](app/views/business_platform/dic_ticket_api.py#L128)
* PUT [/api/dic/ticket/<string:ticket_id>](app/views/business_platform/dic_ticket_api.py#L137)
* GET [/api/dic/ticket/list](app/views/business_platform/dic_ticket_api.py#L182)
* GET [/api/dic/ticket/<string:ticket_id>](app/views/business_platform/dic_ticket_api.py#L213)
* GET [/api/dic/ticket/permission/<string:page_title>](app/views/business_platform/dic_ticket_api.py#L228)
* POST [/api/dic/ticket/<string:ticket_id>/task](app/views/business_platform/dic_ticket_api.py#L269)
* GET [/api/dic/ticket/<string:ticket_id>/task](app/views/business_platform/dic_ticket_api.py#L296)
* GET [/api/dic/ticket/project/list](app/views/business_platform/dic_ticket_api.py#L313)
* POST [/api/dic/ticket/<string:ticket_id>/message](app/views/business_platform/dic_ticket_api.py#L324)
* GET [/api/dic/ticket/<string:ticket_id>/message](app/views/business_platform/dic_ticket_api.py#L349)
  

`dic_ticket:all`
* GET [/api/dic/ticket/functional_module/list](app/views/business_platform/dic_ticket_api.py#L76)
* POST [/api/dic/ticket](app/views/business_platform/dic_ticket_api.py#L88)
* DELETE [/api/dic/ticket/<string:ticket_id>](app/views/business_platform/dic_ticket_api.py#L128)
* PUT [/api/dic/ticket/<string:ticket_id>](app/views/business_platform/dic_ticket_api.py#L137)
* GET [/api/dic/ticket/list](app/views/business_platform/dic_ticket_api.py#L182)
* GET [/api/dic/ticket/<string:ticket_id>](app/views/business_platform/dic_ticket_api.py#L213)
* GET [/api/dic/ticket/permission/<string:page_title>](app/views/business_platform/dic_ticket_api.py#L228)
* GET [/api/dic/ticket/project/list](app/views/business_platform/dic_ticket_api.py#L313)
* POST [/api/dic/ticket/<string:ticket_id>/message](app/views/business_platform/dic_ticket_api.py#L324)
* GET [/api/dic/ticket/<string:ticket_id>/message](app/views/business_platform/dic_ticket_api.py#L349)
  

`sework.eco.task:add`
* POST [/api/presales/eco_partner/task](app/views/business_platform/ecopartner_api.py#L49)
  

`sework.eco:all`
* POST [/api/presales/eco_partner/task/<task_id>/sub_task](app/views/business_platform/ecopartner_api.py#L110)
* GET [/api/presales/eco_partner/task/<task_id>](app/views/business_platform/ecopartner_api.py#L184)
* DELETE [/api/presales/eco_partner/task/<task_id>](app/views/business_platform/ecopartner_api.py#L232)
* PUT [/api/presales/eco_partner/task/<task_id>/archive](app/views/business_platform/ecopartner_api.py#L277)
* GET [/api/presales/eco_partner/tasks](app/views/business_platform/ecopartner_api.py#L348)
* GET [/api/presales/eco_partner/tasks/partners](app/views/business_platform/ecopartner_api.py#L425)
* GET [/api/presales/eco_partner/record/pending_approval](app/views/business_platform/ecopartner_api.py#L493)
* GET [/api/presales/eco_partner/task/support_type](app/views/business_platform/ecopartner_api.py#L532)
* GET [/api/presales/eco_partner/permission/<page_title>](app/views/business_platform/ecopartner_api.py#L550)
* POST [/api/presales/eco_partner/task/<task_id>/record](app/views/business_platform/ecopartner_api.py#L589)
* PUT [/api/presales/eco_partner/record/<record_id>](app/views/business_platform/ecopartner_api.py#L729)
* DELETE [/api/presales/eco_partner/record/<record_id>](app/views/business_platform/ecopartner_api.py#L845)
* GET [/api/presales/eco_partner/task/<task_id>/record/list](app/views/business_platform/ecopartner_api.py#L864)
* PUT [/api/presales/eco_partner/record/<record_id>/approval](app/views/business_platform/ecopartner_api.py#L948)
  

`sework.internal:all`
* GET [/api/presales/internal_work/project/support_type](app/views/business_platform/internalwork_api.py#L31)
* GET [/api/presales/internal_work/project/list](app/views/business_platform/internalwork_api.py#L115)
* GET [/api/presales/internal_work/project/<project_id>](app/views/business_platform/internalwork_api.py#L203)
* DELETE [/api/presales/internal_work/project/<project_id>](app/views/business_platform/internalwork_api.py#L241)
* GET [/api/presales/internal_work/project/owner/list](app/views/business_platform/internalwork_api.py#L280)
* GET [/api/presales/internal_work/project/create_by/list](app/views/business_platform/internalwork_api.py#L306)
* GET [/api/presales/internal_work/project/participants/list](app/views/business_platform/internalwork_api.py#L332)
* GET [/api/presales/internal_work/project/<project_id>/participants/list](app/views/business_platform/internalwork_api.py#L359)
* PUT [/api/presales/internal_work/project/<project_id>/archive](app/views/business_platform/internalwork_api.py#L415)
* POST [/api/presales/internal_work/task](app/views/business_platform/internalwork_api.py#L463)
* GET [/api/presales/internal_work/task/list](app/views/business_platform/internalwork_api.py#L522)
* GET [/api/presales/internal_work/task/<task_id>](app/views/business_platform/internalwork_api.py#L606)
* DELETE [/api/presales/internal_work/task/<task_id>](app/views/business_platform/internalwork_api.py#L646)
* POST [/api/presales/internal_work/task/<task_id>/subtask](app/views/business_platform/internalwork_api.py#L674)
* PUT [/api/presales/internal_work/task/<task_id>/archive](app/views/business_platform/internalwork_api.py#L744)
* POST [/api/presales/internal_work/task/<task_id>/record](app/views/business_platform/internalwork_api.py#L815)
* PUT [/api/presales/internal_work/task/<task_id>/record/<record_id>](app/views/business_platform/internalwork_api.py#L933)
* GET [/api/presales/internal_work/task/<task_id>/record/list](app/views/business_platform/internalwork_api.py#L1053)
* GET [/api/presales/internal_work/permission/<page_title>](app/views/business_platform/internalwork_api.py#L1143)
  

`sework.internal.project:add`
* POST [/api/presales/internal_work/project](app/views/business_platform/internalwork_api.py#L56)
* GET [/api/presales/internal_work/record/pending](app/views/business_platform/internalwork_api.py#L1187)
* GET [/api/presales/internal_work/record/<record_id>](app/views/business_platform/internalwork_api.py#L1227)
* PUT [/api/presales/internal_work/record/<record_id>/approval](app/views/business_platform/internalwork_api.py#L1294)
  

`business_leads:list`
* GET [/api/business/leads](app/views/business_platform/leads_api.py#L48)
* GET [/api/business/leads/detail/<_id>](app/views/business_platform/leads_api.py#L239)
  

`business_leads:mutation`
* POST [/api/business/leads](app/views/business_platform/leads_api.py#L71)
* PUT [/api/business/leads/push/<_id>](app/views/business_platform/leads_api.py#L142)
  

`se.project_manage:list`
* GET [/api/presales/project_manage/project](app/views/business_platform/projectmanage_api.py#L198)
* GET [/api/presales/project_manage/record/pending](app/views/business_platform/projectmanage_api.py#L293)
* GET [/api/presales/project_manage/record/<record_id>](app/views/business_platform/projectmanage_api.py#L336)
* PUT [/api/presales/project_manage/record/<record_id>/approval](app/views/business_platform/projectmanage_api.py#L404)
* GET [/api/presales/project_manage/project/<project_id>](app/views/business_platform/projectmanage_api.py#L551)
* PUT [/api/presales/project_manage/project/<project_id>](app/views/business_platform/projectmanage_api.py#L596)
* GET [/api/presales/project_manage/project/<project_id>/task_statistics](app/views/business_platform/projectmanage_api.py#L701)
* GET [/api/presales/project_manage/project/<project_id>/task](app/views/business_platform/projectmanage_api.py#L745)
* GET [/api/presales/project_manage/project/<project_id>/task/approval](app/views/business_platform/projectmanage_api.py#L832)
* PUT [/api/presales/project_manage/task/<task_id>/approval](app/views/business_platform/projectmanage_api.py#L925)
* PUT [/api/presales/project_manage/task/<task_id>/receive](app/views/business_platform/projectmanage_api.py#L1046)
* GET [/api/presales/project_manage/task/support_type](app/views/business_platform/projectmanage_api.py#L1152)
* POST [/api/presales/project_manage/task/<main_task_id>/subtask](app/views/business_platform/projectmanage_api.py#L1180)
* GET [/api/presales/project_manage/task/<task_id>](app/views/business_platform/projectmanage_api.py#L1250)
* DELETE [/api/presales/project_manage/task/<task_id>](app/views/business_platform/projectmanage_api.py#L1295)
* POST [/api/presales/project_manage/task/<task_id>/record](app/views/business_platform/projectmanage_api.py#L1329)
* PUT [/api/presales/project_manage/record/<record_id>](app/views/business_platform/projectmanage_api.py#L1485)
* DELETE [/api/presales/project_manage/record/<record_id>](app/views/business_platform/projectmanage_api.py#L1614)
* GET [/api/presales/project_manage/task/<task_id>/record](app/views/business_platform/projectmanage_api.py#L1639)
* GET [/api/presales/project_manage/permission/<page_title>](app/views/business_platform/projectmanage_api.py#L1736)
* PUT [/api/presales/project_manage/task/<task_id>/archive](app/views/business_platform/projectmanage_api.py#L1818)
* PUT [/api/presales/project_manage/project/<project_id>/archive](app/views/business_platform/projectmanage_api.py#L1927)
* GET [/api/presales/project_manage/project/owner/list](app/views/business_platform/projectmanage_api.py#L2014)
* GET [/api/presales/project_manage/project/create_by/list](app/views/business_platform/projectmanage_api.py#L2040)
* GET [/api/presales/project_manage/project/participants/list](app/views/business_platform/projectmanage_api.py#L2066)
* GET [/api/presales/project_manage/project/<project_id>/participants/list](app/views/business_platform/projectmanage_api.py#L2093)
* GET [/api/presales/project_manage/project/<project_id>/products](app/views/business_platform/projectmanage_api.py#L2150)
* GET [/api/presales/project_manage/archive/task/list](app/views/business_platform/projectmanage_api.py#L2183)
* GET [/api/presales/project_manage/enable/task/list](app/views/business_platform/projectmanage_api.py#L2228)
* GET [/api/presales/project_manage/opportunity/status](app/views/business_platform/projectmanage_api.py#L2273)
  

`se.weekly:list`
* POST [/api/presales/weekly](app/views/business_platform/seweekly_api.py#L36)
* GET [/api/presales/weekly/list](app/views/business_platform/seweekly_api.py#L77)
* GET [/api/presales/weekly/<weekly_id>](app/views/business_platform/seweekly_api.py#L118)
* POST [/api/presales/weekly/<weekly_id>](app/views/business_platform/seweekly_api.py#L155)
* PUT [/api/presales/weekly/<weekly_id>](app/views/business_platform/seweekly_api.py#L201)
* DELETE [/api/presales/weekly/<weekly_id>](app/views/business_platform/seweekly_api.py#L228)
* GET [/api/presales/weekly/template/data](app/views/business_platform/seweekly_api.py#L252)
* GET [/api/presales/weekly/template/new/data](app/views/business_platform/seweekly_api.py#L313)
* GET [/api/presales/weekly/not_send](app/views/business_platform/seweekly_api.py#L344)
  

`support.call_record:list`
* GET [/api/support/aliyun_ccc/agent](app/views/communication_platform/agent_api.py#L22)
* GET [/api/support/aliyun_ccc/call_record](app/views/communication_platform/call_api.py#L27)
* GET [/api/support/aliyun_ccc/call_record/mono_recording](app/views/communication_platform/call_api.py#L69)
  

`internal.api:list`
* GET [/api/aggregated_search/site_list](app/views/st_serach/st_api.py#L30)
* POST [/api/aggregated_search/search_info](app/views/st_serach/st_api.py#L49)
* POST [/api/aggregated_search/site/visit](app/views/st_serach/st_api.py#L64)
* GET [/api/aggregated_search/analyze](app/views/st_serach/st_api.py#L79)
* GET [/api/aggregated_search/overview](app/views/st_serach/st_api.py#L95)
* GET [/api/aggregated_search/detail](app/views/st_serach/st_api.py#L116)
* GET [/api/internal/crm/customer](app/views/sys_internal/crm_api.py#L24)
* GET [/api/internal/crm/customer/<customer_id>](app/views/sys_internal/crm_api.py#L42)
* GET [/api/internal/crm/sysuser](app/views/sys_internal/crm_api.py#L68)
* GET [/api/internal/crm/sysuser/<user_id>](app/views/sys_internal/crm_api.py#L87)
* GET [/api/internal/crm/my_assignable_se_staff](app/views/sys_internal/crm_api.py#L102)
* GET [/api/internal/hr/staff/list](app/views/sys_internal/hr_api.py#L22)
* GET [/api/internal/user/<user_id>/department](app/views/sys_internal/internal_api.py#L20)
* GET [/api/internal/manage/department](app/views/sys_internal/internal_api.py#L52)
* GET [/api/internal/person/info](app/views/sys_internal/internal_api.py#L89)
* PUT [/api/internal/person/info](app/views/sys_internal/internal_api.py#L144)
* GET [/api/internal/district/list](app/views/sys_internal/internal_api.py#L163)
  

`department:list`
* GET [/api/sys/department](app/views/sys_manage/department_api.py#L23)
  

`employee:list`
* GET [/api/sys/department](app/views/sys_manage/department_api.py#L67)
* GET [/api/sys/role/<role_id>/employee](app/views/sys_manage/role_api.py#L473)
* GET [/api/sys/user](app/views/sys_manage/user_api.py#L32)
* GET [/api/sys/user/employee/list/<role_id>](app/views/sys_manage/user_api.py#L64)
* GET [/api/sys/user/employee/<user_id>](app/views/sys_manage/user_api.py#L103)
  

`field:mutation`
* POST [/api/sys/fields](app/views/sys_manage/fields_api.py#L70)
* PUT [/api/sys/fields/<fields_id>](app/views/sys_manage/fields_api.py#L101)
* DELETE [/api/sys/fields/<fields_id>](app/views/sys_manage/fields_api.py#L125)
* POST [/api/sys/fields](app/views/sys_manage/fields_api.py#L158)
* PUT [/api/sys/fields/subsystem/<subsystem_id>](app/views/sys_manage/fields_api.py#L199)
* POST [/api/sys/fields/subsystem/<subsystem_id>](app/views/sys_manage/fields_api.py#L212)
* DELETE [/api/sys/fields/subsystem/<subsystem_id>](app/views/sys_manage/fields_api.py#L229)
* PUT [/api/sys/fields/recycle/<delete_id>](app/views/sys_manage/fields_api.py#L329)
  

`field:list`
* GET [/api/sys/fields](app/views/sys_manage/fields_api.py#L143)
* GET [/api/sys/fields/object/<subsystem_id>](app/views/sys_manage/fields_api.py#L180)
* GET [/api/sys/fields/<subsystem_id>/list](app/views/sys_manage/fields_api.py#L251)
* GET [/api/sys/fields](app/views/sys_manage/fields_api.py#L290)
  

`menu:list`
* GET [/api/sys/menu](app/views/sys_manage/menu_api.py#L29)
* GET [/api/sys/menu](app/views/sys_manage/menu_api.py#L70)
* GET [/api/sys/role/<role_id>/permission](app/views/sys_manage/role_api.py#L140)
  

`menu:mutation`
* POST [/api/sys/menu](app/views/sys_manage/menu_api.py#L186)
* DELETE [/api/sys/menu](app/views/sys_manage/menu_api.py#L214)
* PUT [/api/sys/menu/permission/<permission_id>](app/views/sys_manage/menu_api.py#L240)
  

`role:list`
* GET [/api/sys/menu/permission/<permission_id>/role](app/views/sys_manage/menu_api.py#L296)
* GET [/api/sys/role](app/views/sys_manage/role_api.py#L42)
* GET [/api/sys/role/<role_id>/user](app/views/sys_manage/role_api.py#L285)
* GET [/api/sys/user/local/<user_id>/role](app/views/sys_manage/user_api.py#L251)
  

`user:list`
* GET [/api/sys/menu/permission/<permission_id>/user](app/views/sys_manage/menu_api.py#L334)
* GET [/api/sys/user](app/views/sys_manage/user_api.py#L145)
* GET [/api/sys/user/local/list/<role_id>](app/views/sys_manage/user_api.py#L189)
* GET [/api/sys/user/local/<user_id>](app/views/sys_manage/user_api.py#L225)
  

`sys.resource:all`
* POST [/api/sys/resource](app/views/sys_manage/resource_api.py#L37)
* GET [/api/sys/resource](app/views/sys_manage/resource_api.py#L80)
* PUT [/api/sys/resource/<resource_id>](app/views/sys_manage/resource_api.py#L117)
  

`role:mutation`
* POST [/api/sys/role](app/views/sys_manage/role_api.py#L65)
* DELETE [/api/sys/role](app/views/sys_manage/role_api.py#L81)
* PUT [/api/sys/role/<role_id>](app/views/sys_manage/role_api.py#L107)
* PUT [/api/sys/role/<role_id>/permission](app/views/sys_manage/role_api.py#L166)
* PUT [/api/sys/role/<role_id>/local](app/views/sys_manage/role_api.py#L336)
* PUT [/api/sys/role/<role_id>/employee](app/views/sys_manage/role_api.py#L383)
* POST [/api/sys/role/<role_id>/copy](app/views/sys_manage/role_api.py#L504)
* PUT [/api/sys/role/<role_id>/employee/bind](app/views/sys_manage/role_api.py#L546)
* PUT [/api/sys/role/<role_id>/local/bind](app/views/sys_manage/role_api.py#L655)
* PUT [/api/sys/user/local/<user_id>/role](app/views/sys_manage/user_api.py#L267)
  

`user:mutation`
* PUT [/api/sys/user](app/views/sys_manage/user_api.py#L172)
