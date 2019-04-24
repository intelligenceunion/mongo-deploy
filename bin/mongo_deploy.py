import argparse
from iu_mongo_deploy.replicaset.utils import start_replica, stop_replica

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('command', choices=['start', 'stop'])
    arg_parser.add_argument('env')
    arg_parser.add_argument('replica')
    arg_parser.add_argument('--auth', action='store_false', default=False)
    arg_parser.add_argument('--node', type=int, default=None)
    arg_parser.add_argument('--port', type=int, default=27017)
    args = arg_parser.parse_args()
    start_kwargs = {}
    stop_kwargs = {}
    if args.auth:
        start_kwargs.update({'auth': args.auth})
    if args.node:
        start_kwargs.update({'node': args.node})
        stop_kwargs.update({'node': args.node})
    if args.port:
        start_kwargs.update({'port': args.port})
    if args.command == 'start':
        start_replica(args.env, args.replica, **start_kwargs)
    else:
        stop_replica(args.env, args.replica, **stop_kwargs)
