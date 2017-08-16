from tiles.alg.TILES import TILES
from tiles.alg.eTILES import eTILES
import sys
import argparse

__author__ = "Giulio Rossetti"
__contact__ = "giulio.rossetti@gmail.com"
__website__ = "about.giuliorossetti.net"
__license__ = "BSD"

if __name__ == "__main__":

    sys.stdout.write("------------------------------------\n")
    sys.stdout.write("              TILES                 \n")
    sys.stdout.write("------------------------------------\n")
    sys.stdout.write("Author: " + __author__ + "\n")
    sys.stdout.write("Email:  " + __contact__ + "\n")
    sys.stdout.write("WWW:    " + __website__ + "\n")
    sys.stdout.write("------------------------------------\n")

    parser = argparse.ArgumentParser()

    parser.add_argument('filename', type=str, help='filename')
    parser.add_argument('-o', '--obs', type=int, help='observation (days)', default=7)
    parser.add_argument('-p', '--path', type=str, help='path', default="")
    parser.add_argument('-t', '--ttl', type=int, help='Edge Time To Leave (optional)', default=float('inf'))
    parser.add_argument('-m', '--mode', type=str, help='TTL or Explicit', default="TTL")

    args = parser.parse_args()

    if args.mode == 'TTL':
        an = TILES(filename=args.filename, obs=args.obs, path=args.path, ttl=args.ttl)
        an.execute()
    elif args.mode == 'Explicit':
        an = eTILES(filename=args.filename, obs=args.obs, path=args.path)
        an.execute()
    else:
        sys.stdout.write("Unsupported mode\n")
        sys.stdout.flush()


