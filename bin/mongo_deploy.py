import argparse
from iu_mongo.replicaset.utils import start_replica, stop_replica

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('command', choices=['start', 'stop'])
    arg_parser.add_argument('env')
    arg_parser.add_argument('replica')
    args = arg_parser.parse_args()
    if args.command == 'start':
        start_replica(args.env, args.replica)
    else:
        stop_replica(args.env, args.replica)
