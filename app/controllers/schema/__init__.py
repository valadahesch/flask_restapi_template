from .techadmin_schema import SysUserSchema, SysCasbinPolicySchema, SysFieldSchema, SysMenuSchema, \
    SysSubsystemObjectSchema, SysRoleUserSchema, TbEmployeeSchema, TblDepartmentSchema, SysRoleMenuSchema, \
    SysRoleSchema, SysFieldPermissionSchema, SysAttachmentSchema, OperateHistorySchema

from .tac_ods_schema import OdsWecomUserSchema, OdsWecomDepartmentSchema

from .se_project_schema import SeProjectProjectSchema, SeProjectTaskSchema, SeProjectRecordSchema, \
    SeProjectApprovalRecordSchema, SeProjectFocusSchema, SeWeeklySchema

from .se_work_schema import SeWorkTaskSchema, SeWorkProjectSchema, SeWorkRecordSchema, SeWorkApprovalRecordSchema

from .business_schema import BusinessLeadSchema

from .eco_partner_schema import SeEcoTaskSchema, SeEcoRecordSchema, SeEcoApprovalRecordSchema

from .online_tools_schema import Conf2HsSchema

from .ps_inspection_schema import PsTaskSchema, PsTaskUploadHistorySchema, PsUserMappingSchema, PsCustomerArchivesSchema

from .file_system_schema import FileManageSchema
