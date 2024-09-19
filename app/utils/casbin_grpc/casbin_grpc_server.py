import grpc
import casbin
import os
import casbin_sqlalchemy_adapter

from app.config import SQLConfig
from app.utils.casbin_grpc.protos import casbin_util_pb2_grpc
from app.utils.casbin_grpc.protos.casbin_util_pb2 import VerifyResult, StringList, EmptyResponse, PermissionResponse
from concurrent import futures


class CasbinUtilServicer(casbin_util_pb2_grpc.CasbinUtilServicer):
    """Provides methods that implement functionality of route guide server."""

    def __init__(self):
        model_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../conf/casbin_model.conf')
        sql_url = SQLConfig['database']
        adapter = casbin_sqlalchemy_adapter.Adapter(sql_url)
        self.ce = casbin.Enforcer(model_path, adapter)

    def enforce(self, request, context):
        if self.ce.enforce(request.user_id, request.permission):
            return VerifyResult(verify_result=True)

        return VerifyResult(verify_result=False)

    def getRolesUser(self, request, context):
        res = self.ce.get_roles_for_user(request.user_id)
        return StringList(items=res)

    def addRoleUser(self, request, context):
        self.ce.add_role_for_user(request.user_id, request.role_id)
        return EmptyResponse()

    def addRule(self, request, context):
        self.ce.add_named_policy('p', request.rule)
        return EmptyResponse()

    def deleteRoleUser(self, request, context):
        self.ce.delete_role_for_user(request.user_id, request.role_id)
        return EmptyResponse()

    def deleteRole(self, request, context):
        self.ce.delete_role(request.role_id)
        return EmptyResponse()

    def deleteRoleMenu(self, request, context):
        self.ce.remove_named_policy('p', request.rule)
        return EmptyResponse()

    def getPermissionByUserId(self, request, context):
        res = self.ce.get_implicit_permissions_for_user(request.user_id)
        response = PermissionResponse()

        for row in res:
            response.row.add().items.extend(row)

        return response


def start_grpc_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    casbin_util_pb2_grpc.add_CasbinUtilServicer_to_server(CasbinUtilServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()