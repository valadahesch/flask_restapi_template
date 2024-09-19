import grpc
from app.utils.casbin_grpc.protos import casbin_util_pb2_grpc
from app.utils.casbin_grpc.protos import casbin_util_pb2


grpc_channel = grpc.insecure_channel("127.0.0.1:50051")
stub = casbin_util_pb2_grpc.CasbinUtilStub(grpc_channel)
res = stub.getPermissionByUserId(casbin_util_pb2.UserId(user_id='bvt7lbrd3m9m90t'))
for row in res.row:
    print(row.items[2])