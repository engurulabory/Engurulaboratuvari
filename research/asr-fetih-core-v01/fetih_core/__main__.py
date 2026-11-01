import argparse
from pathlib import Path
from .core import Core,canonical
from .api import Server

def main():
    p=argparse.ArgumentParser(description='FETİH CORE v0.1 — local source-linked candidate graph')
    sub=p.add_subparsers(dest='cmd',required=True)
    sub.add_parser('verify')
    e=sub.add_parser('export');e.add_argument('--output',required=True)
    s=sub.add_parser('serve');s.add_argument('--port',type=int,default=8765)
    a=p.parse_args();c=Core()
    if a.cmd=='verify':print(canonical({'source_integrity':'PASS','verses':len(c.verses),'records':len(c.records),'human_review':'HOLD'}).decode())
    elif a.cmd=='export':
        # Exclusive creation preserves existing user output.
        with Path(a.output).open('xb') as f:f.write(canonical(c.export())+b'\n')
        print(str(Path(a.output).resolve()))
    else:
        with Server(('127.0.0.1',a.port),c) as srv:
            print(f'FETİH CORE http://127.0.0.1:{srv.server_port} (Ctrl-C to stop)',flush=True)
            try:srv.serve_forever()
            except KeyboardInterrupt:pass

if __name__=='__main__':main()
