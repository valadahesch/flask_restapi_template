#!/usr/bin/env python
import os
from gevent import monkey

APP_ENV = os.environ.get('APP_ENV', 'dev')
APP_SERVER = os.environ.get('APP_SERVER', '')
if APP_ENV != 'dev':
    monkey.patch_all()

from flask_script import Manager
from flask_script.commands import ShowUrls, Clean
from gevent.pywsgi import WSGIServer
from tornado.options import define, options
from app import create_app

# default to dev config because no one should use this in
define("admin_port", default=8000, help="TechAdmin running on this port", type=int)
define('address', default='', help='Listen address')
define('port', type=int, default=8081,  help='Listen port')
define('ssladdress', default='', help='SSL listen address')
define('sslport', type=int, default=4433,  help='SSL listen port')
define('certfile', default='', help='SSL certificate file')
define('keyfile', default='', help='SSL private key file')
define('debug', type=bool, default=True, help='Debug mode')
define('policy', default='warning', help='Missing host key policy, reject|autoadd|warning')
define('hostfile', default='', help='User defined host keys file')
define('syshostfile', default='', help='System wide host keys file')
define('tdstream', default='', help='Trusted downstream, separated by comma')
define('redirect', type=bool, default=True, help='Redirecting http to https')
define('fbidhttp', type=bool, default=True, help='Forbid public plain http incoming requests')
define('xheaders', type=bool, default=True, help='Support xheaders')
define('xsrf', type=bool, default=False, help='CSRF protection')
define('origin', default='same', help='Origin policy')
define('wpintvl', type=float, default=0, help='Websocket ping interval')
define('timeout', type=float, default=3, help='SSH connection timeout')
define('delay', type=float, default=5, help='The delay to call recycle_worker')
define('maxconn', type=int, default=5, help='Maximum live connections (ssh sessions) per client')
define('font', default='', help='custom font filename')
define('encoding', default='', help='The default character encoding of ssh servers.')


Other_Server = ["webagent", "grpc_server"]
config_object = 'app.config.%sConfig' % APP_ENV.capitalize() if APP_SERVER not in Other_Server else None
flask_app = create_app(config_object)

manager = Manager(flask_app)
manager.add_command("show-urls", ShowUrls())
manager.add_command("clean", Clean())


@manager.command
def server():
    if flask_app.debug:
        flask_app.run(host='0.0.0.0', port=options.admin_port)
    else:
        http_server = WSGIServer(('0.0.0.0', options.admin_port), flask_app)
        http_server.serve_forever()


@manager.command
def grpc_server():
    from app.utils.casbin_grpc.casbin_grpc_server import start_grpc_server
    start_grpc_server()


@manager.command
def webagent():
    from webagent.main import agent_app
    agent_app()


@manager.command
def cloudlab_deploy_instance():
    from app.utils.kvm.deploy_instance import deploy_instance
    deploy_instance()


@manager.command
def cloudlab_initialize_node_configuration():
    from app.utils.kvm.initialize_node import initialize_node_configuration
    initialize_node_configuration()


@manager.command
def async_cloudlab_delete():
    from app.utils.kvm.async_delete import listen_instance
    listen_instance()


@manager.command
def app_test():
    import unittest
    import coverage

    test_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests")
    cov = coverage.Coverage()
    cov.start()

    start_path = [
        test_path, os.path.join(test_path, "test_api"), os.path.join(test_path, "test_models")
    ]
    for path in start_path:
        unit_suite = unittest.TestLoader().discover(
            start_dir=path, pattern='test*.py', top_level_dir=path
        )
        unittest.TextTestRunner(verbosity=2).run(unit_suite)

    cov.stop()
    cov.save()
    omit = '/root/.local/lib/python3.9/site-packages/*'
    cov.report(omit=omit)
    cov.html_report(directory=f'{test_path}/coverage_report', omit=omit)


@manager.command
def generate_rbac():
    from app.controllers.dao import SysCasbinPolicyDao
    from app.controllers.schema import SysCasbinPolicySchema
    policy = SysCasbinPolicyDao.generateCasbinPolicy()
    casbin_policy = SysCasbinPolicySchema()
    policy = casbin_policy.load(policy, many=True)
    for p in policy:
        SysCasbinPolicyDao.addCasbinPolicy(p)


@manager.command
def permission_list():
    import re
    from app.extensions import permission
    for k, v in permission.permission_api.items():
        print(f'`{k}`', end='\n')
        for url in v:
            endpoint = re.search(r'\[(.*?)\]', url).group(1)
            for rule in flask_app.url_map.iter_rules(endpoint=endpoint):
                url = url.replace(endpoint, rule.rule)
            print(f'* {url}', end='\n')
        print('  \n')


if __name__ == "__main__":
    manager.run(default_command='server')
