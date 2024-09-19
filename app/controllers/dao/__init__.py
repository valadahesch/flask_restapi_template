from .techadmin_dao import SysUserDao, SysRoleUserDao, SysFieldDao, SysSubsystemObjectDao, SysCasbinPolicyDao, \
    SysRoleMenuDao, SysMenuDao, SysRoleDao, TblEmployeeDao, TblDepartmentDao, SysFieldPermissionDao, SysAttachmentDao, \
    OperateHistoryDao

from .tac_ods_dao import TacOdsWeComUserDao, TacOdsWeComDepartmentDao

from .crm_view_dao import CrmViewsDao

from .se_work_dao import SeWorkProjectDao, SeWorkTaskDao, SeWorkRecordDao, SeWorkApprovalDao

from .se_project_dao import SeProjectProjectDao, SeProjectTaskDao, SeProjectRecordDao, SeProjectApprovalDao, \
    SeProjectFocusDao, SeWeeklyDao

from .data_scope_dao import DataScopeDao

from .business_dao import BusinessLeadDao

from .eco_partner_dao import SeEcoRecordDao, SeEcoTaskDao, SeEcoApprovalDao

from .online_tools_dao import AuxiliaryConf2HSDao

from .project_system_dao import MainCollectFieldDao, MainInventoryDao, ProjectMainDao, FieldCustomValueDao, UserMainDao

from .ps_inspection_dao import PsCustomerArchivesDao, PsTaskDao, PsTaskUploadHistoryDao, PsUserMappingDao

from .file_system_dao import SysFileManageDao