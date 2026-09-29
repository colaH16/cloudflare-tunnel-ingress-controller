#!/usr/bin/env python3
"""Probe only a user-provided static echo test hostname; save no arbitrary bodies."""
import argparse,json,subprocess,time
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('hostname');parser.add_argument('--output',type=Path);args=parser.parse_args()
paths=['/','/wp-admin','/wp-admin/','/wp-admin/edit.php','/foo/wp-admin/','/wp-admin-other/','/WP-ADMIN/','/v1.0','/v1.0/users','/v1X0','/prefix/v1.0','/legacy/admin','/legacy/login','/foo/legacy/admin','/legacy/admin/edit','/admin','/admin/','/admin/settings','/admin-tools','/prefix/admin']
rows=[]
for path in paths:
    p=subprocess.run(['curl','--silent','--show-error','--path-as-is','--max-time','20','--header','Cache-Control: no-cache','--write-out','\n%{http_code}','https://'+args.hostname+path+'?pr368_probe='+str(time.time_ns())],capture_output=True,text=True)
    body,_,status=p.stdout.strip().rpartition('\n');body=body.strip()
    if p.returncode or status!='200' or body not in ('PUBLIC','ADMIN','LITERAL'):
        raise SystemExit('Unexpected response at '+path+'; HTTP '+status+'; body omitted')
    row={'path':path,'status':status,'backend':body};rows.append(row);print(path,status,body)
if args.output:args.output.write_text(json.dumps(rows,indent=2)+'\n')
