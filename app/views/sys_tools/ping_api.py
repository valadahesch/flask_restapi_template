from flask import Blueprint, request, jsonify
from flask_restful import Resource
from app.utils.api_util import Api, AppResponse
from app.extensions import logger


ping_app = Blueprint('ping', __name__, url_prefix='/api/ping')
ping_api = Api(ping_app)


@ping_api.resource('')
class PingAPI(Resource):

    def get(self):

        return jsonify(AppResponse(data={"ping": "pong"}))


