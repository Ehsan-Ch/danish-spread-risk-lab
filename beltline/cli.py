import argparse
from .data import download
from .pipeline import run
from .server import serve

def main():
    parser=argparse.ArgumentParser(description='Beltline Danish spread research')
    sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('download');p.add_argument('--cache',default='data')
    p=sub.add_parser('run');p.add_argument('--cache',default='data');p.add_argument('--output',default='reports/custom')
    p=sub.add_parser('serve');p.add_argument('--port',type=int,default=8790)
    a=parser.parse_args()
    if a.command=='download':download(a.cache)
    elif a.command=='run':run(a.cache,a.output)
    else:serve(a.port)

if __name__=='__main__':main()
