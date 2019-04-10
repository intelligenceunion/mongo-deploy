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


def start_replica(env, replica, auth=True):
    try:
        replica_config = __CONFIGS[env][replica]
    except Exception:
        raise ConfigNotFoundException(
            'Confiugration not found for replica "%s" and env "%s"' % (replica, env))
    container_name = volume_name = replica_name = replica_config.name
    mongo_version = replica_config.mongo_version
    client = docker.from_env()
    try:
        if client.containers.get(container_name):
            raise ContainerExistException(
                'Container "%s" with name exists.' % container_name)
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
                                      ports={"27017": "27017"},
                                      name=container_name)
    return container


def stop_replica(env, replica):
    try:
        replica_config = __CONFIGS[env][replica]
    except Exception:
        raise ConfigNotFoundException(
            'Confiugration not found for replica "%s" and env "%s"' % (replica, env))
    container_name = replica_config.name
    client = docker.from_env()
    try:
        container = client.containers.get(container_name)
        container.stop()
        container.remove()
    except docker.errors.NotFound:
        pass
