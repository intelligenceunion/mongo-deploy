import docker
import os
from docker.types import Mount
from collections import namedtuple

ReplicaConfig = namedtuple('ReplicaConfig', ['name', 'mongo_version'])
__CONFIGS = {
    'stage': {
        'rs1': ReplicaConfig(name='default_stage_rs1', mongo_version='4.0')
    }
}


class ConfigNotFoundException(Exception):
    pass


class ContainerExistException(Exception):
    pass


def start_replica(env, replica, auth=False, node=None, port=27017):
    try:
        replica_config = __CONFIGS[env][replica]
    except Exception:
        raise ConfigNotFoundException(
            'Confiugration not found for replica "%s" and env "%s"' % (replica, env))
    replica_name = replica_config.name
    if node is not None:
        volume_name = container_name = replica_name+'_node%d' % node
    else:
        volume_name = container_name = replica_name
    mongo_version = replica_config.mongo_version
    client = docker.from_env()
    try:
        container = client.containers.get(container_name)
        if container:
            print('Container "%s" with name exists, remove it first...' %
                  container_name)
            container.stop()
            container.remove()
    except docker.errors.NotFound:
        pass
    data_mount = Mount(
        target='/data/db',
        source=volume_name,
    )
    config_mount = Mount(
        target='/data/configdb',
        source='configdb_empty'
    )
    command = [
        'mongod'
    ]
    if auth:
        command.append('--auth')
    command.extend([
        '--replSet',
        replica_name
    ])
    container = client.containers.run('mongo:%s' % mongo_version,
                                      detach=True,
                                      command=command,
                                      mounts=[data_mount, config_mount],
                                      ports={"27017": str(port)},
                                      name=container_name)
    return container


def stop_replica(env, replica, node=None):
    try:
        replica_config = __CONFIGS[env][replica]
    except Exception:
        raise ConfigNotFoundException(
            'Confiugration not found for replica "%s" and env "%s"' % (replica, env))
    if node is not None:
        container_name = replica_config.name+'_node%d' % node
    else:
        container_name = replica_config.name
    client = docker.from_env()
    try:
        container = client.containers.get(container_name)
        container.stop()
        container.remove()
    except docker.errors.NotFound:
        pass
