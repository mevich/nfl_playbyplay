from invoke import task
from fabric import Connection


@task
def dev(context):
	context.user = "ubuntu"
	context.path = "/mnt/nflpbp"
	context.branch = "master"
	context.host = "54.200.129.30"
	context.forward_agent = True

@task
def test(context):
	context.user = "ubuntu"
	context.path = "/whtever/path"
	context.branch = "dev"
	context.host = "XxXX"
	context.forward_agent = True


def _update_code(connection, context):
	with connection.cd(context.path):
		connection.run("git pull origin {}".format(context.branch))
		connection.run("/home/ubuntu/.local/bin/pip install -r requirements.txt")
		connection.run("supervisorctl restart python")


@task
def deploy(context):
	connection = Connection(context.host, config=context.config)
	_update_code(connection, context)
