#!/usr/bin/env python3
import csv, sys
from collections import defaultdict

def load(path):
    with open(path,newline='') as f:
        rows=list(csv.DictReader(f))
    for i,r in enumerate(rows, start=2):
        r['_line']=i
        r['MOB_Start']=int(float(r['MOB_Start']))
        r['MOB_End']=int(float(r['MOB_End']))
    return rows

def overlaps(a,b):
    return not (a['MOB_End']<b['MOB_Start'] or b['MOB_End']<a['MOB_Start'])

def main(path):
    rows=load(path)
    buckets=defaultdict(list)
    for r in rows:
        key=(r['Segment'],r['Cohort'],r['Metric'])
        buckets[key].append(r)
    issues=[]
    for key,arr in buckets.items():
        arr=sorted(arr,key=lambda x:(x['MOB_Start'],x['MOB_End'],x['_line']))
        for i in range(len(arr)):
            for j in range(i+1,len(arr)):
                if overlaps(arr[i],arr[j]):
                    issues.append((key,arr[i],arr[j]))
    print(f"{path}: {len(rows)} rows, {len(issues)} overlap(s) within identical Segment/Cohort/Metric keys")
    for key,a,b in issues[:20]:
        print(' ',key,f"line {a['_line']} [{a['MOB_Start']}-{a['MOB_End']}] vs line {b['_line']} [{b['MOB_Start']}-{b['MOB_End']}]")
    if len(issues)>20:
        print('  ...')
    return 1 if issues else 0

if __name__=='__main__':
    rc=0
    for p in sys.argv[1:]:
        rc |= main(p)
    sys.exit(rc)
