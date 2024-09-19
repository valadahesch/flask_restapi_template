import os
import sys
import inspect
import importlib

from flask import Flask
from flask_session import Session
from flask_cors import CORS


def initialize_tracer(flask_app):
    import platform
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter as OTLPSpanHttpExporter
    from opentelemetry.sdk.resources import DEPLOYMENT_ENVIRONMENT, HOST_NAME, Resource, SERVICE_NAME, SERVICE_VERSION
    from opentelemetry.instrumentation.flask import FlaskInstrumentor
    from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
    from opentelemetry.instrumentation.requests import RequestsInstrumentor
    from opentelemetry.instrumentation.elasticsearch import ElasticsearchInstrumentor
    from opentelemetry.instrumentation.redis import RedisInstrumentor
    resource = Resource(attributes={
        SERVICE_NAME: "techadmin-server",
        SERVICE_VERSION: "",
        DEPLOYMENT_ENVIRONMENT: "",
        HOST_NAME: platform.node()
    })
    span_processor = BatchSpanProcessor(OTLPSpanHttpExporter(
        endpoint=flask_app.config["TRACE_ENDPOINT"]
    ))

    trace_provider = TracerProvider(resource=resource, active_span_processor=span_processor)
    trace.set_tracer_provider(trace_provider)

    SQLAlchemyInstrumentor().instrument()
    RequestsInstrumentor().instrument()
    ElasticsearchInstrumentor().instrument()
    RedisInstrumentor().instrument()
    FlaskInstrumentor().instrument_app(flask_app)


def create_app(config_object=None):
    flask_app = Flask(__name__)
    if not config_object:
        return flask_app

    from app.utils.api_util import Api, CustomJSONEncoder
    flask_app.json_encoder = CustomJSONEncoder
    flask_app.jinja_env.auto_reload = True
    flask_app.config.from_object(config_object)

    if flask_app.config["ENV"] == 'prod':
        initialize_tracer(flask_app=flask_app)
    else:
        from flasgger import Swagger
        from app.extensions import debug_toolbar
        debug_toolbar.init_app(flask_app)
        if "SWAGGER_CONFIG" in flask_app.config:
            Swagger(flask_app, config=flask_app.config["SWAGGER_CONFIG"])

    # flask-restful
    Api().init_app(flask_app)
    Session(flask_app)
    CORS(flask_app, origins="*", allow_headers=[
        "Authorization", "Content-Type", "X-Permission", "X-User-Id", "X-Platform", "Access-Control-Allow-Origin",
        "X-Real-User-Id"
    ])

    # initialize SQLAlchemy
    from app.models import db
    db.init_app(flask_app)

    from app.extensions import redis_client, cache, permission
    # 缓存使用本地Redis或者本地字典存储
    cache.init_app(flask_app)
    redis_client.init_app(flask_app)
    # 初始化权限
    with flask_app.app_context():
        permission.init_app(db.get_engine())

    # register all blueprints and api(s)
    views_path = os.path.join(os.path.dirname(__file__), 'views')
    for root, dirs, files in os.walk(views_path):
        sys.path.insert(0, root)
        for name in files:
            if not name.endswith('_api.py'):
                continue

            if flask_app.config.get("DISABLEPATH"):
                if name in flask_app.config.get("DISABLEPATH"):
                    continue

            app_name = name.rsplit('_', 1)[0] + '_app'
            f = os.path.join(root, name)
            module = inspect.getmodulename(f)
            flask_app.register_blueprint(getattr(importlib.import_module(module), app_name))
        sys.path.remove(root)

    return flask_app
