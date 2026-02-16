#!/usr/bin/env python3
"""Generate cohort-specific Manual Coll_Principal methodology rows from backtest.

For selected months, this script:
1) ranks Segment×Cohort by abs variance in Coll_Principal,
2) picks top N negative-variance drivers,
3) computes target rate per month = Actual Coll_Principal / Forecast OpeningGBV,
4) outputs Manual rows with MOB_Start=MOB_End for those exact months.
"""
import argparse
import csv
import zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime, timedelta

NS = {
    'a': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
    'p': 'http://schemas.openxmlformats.org/package/2006/relationships',
}


def load_shared_strings(zf):
    if 'xl/sharedStrings.xml' not in zf.namelist():
        return []
    root = ET.fromstring(zf.read('xl/sharedStrings.xml'))
    return [''.join(t.text or '' for t in si.findall('.//a:t', NS)) for si in root.findall('a:si', NS)]


def sheet_path_by_name(zf, name):
    wb = ET.fromstring(zf.read('xl/workbook.xml'))
    rels = ET.fromstring(zf.read('xl/_rels/workbook.xml.rels'))
    rmap = {r.attrib['Id']: r.attrib['Target'] for r in rels.findall('p:Relationship', NS)}
    for sh in wb.find('a:sheets', NS):
        if sh.attrib.get('name') == name:
            rid = sh.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
            return 'xl/' + rmap[rid]
    raise ValueError(f"Sheet not found: {name}")


def read_backtest_rows(xlsx_path):
    with zipfile.ZipFile(xlsx_path) as zf:
        shared = load_shared_strings(zf)
        sheet = sheet_path_by_name(zf, '14_Backtest_Comparison')
        root = ET.fromstring(zf.read(sheet))

    rows = root.findall('.//a:sheetData/a:row', NS)
    header = []
    for c in rows[0].findall('a:c', NS):
        v = c.find('a:v', NS)
        x = v.text if v is not None else ''
        if c.attrib.get('t') == 's':
            x = shared[int(x)]
        header.append(x)

    base = datetime(1899, 12, 30)
    out = []
    for row in rows[1:]:
        vals = {}
        for c in row.findall('a:c', NS):
            col = ''.join(ch for ch in c.attrib.get('r', '') if ch.isalpha())
            v = c.find('a:v', NS)
            if v is None:
                continue
            x = v.text
            if c.attrib.get('t') == 's':
                x = shared[int(x)]
            vals[col] = x
        rec = dict(zip(header, [vals.get(c, '') for c in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']]))
        if not rec.get('Segment'):
            continue
        rec['MonthStr'] = (base + timedelta(days=int(float(rec['Month'])))).strftime('%Y-%m')
        out.append(rec)
    return out


def mob_for(cohort, monthstr):
    cy = int(cohort[:4])
    cm = int(cohort[4:6])
    my = int(monthstr[:4])
    mm = int(monthstr[5:7])
    return (my - cy) * 12 + (mm - cm) + 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--xlsx', default='BB Forecast V5.2.xlsx')
    ap.add_argument('--months', default='2025-10,2025-11', help='Comma-separated YYYY-MM list')
    ap.add_argument('--top-n', type=int, default=5)
    ap.add_argument('--out', default='Rate_Methodology_patch_top5_manual_mob_oct_nov.csv')
    args = ap.parse_args()

    months = tuple(m.strip() for m in args.months.split(',') if m.strip())
    rows = read_backtest_rows(args.xlsx)

    variance_rank = defaultdict(float)
    for r in rows:
        if r['Metric'] == 'Coll_Principal' and r['MonthStr'] in months:
            variance_rank[(r['Segment'], r['Cohort'])] += float(r['Variance'])

    top = [k for k, v in sorted(variance_rank.items(), key=lambda kv: abs(kv[1]), reverse=True) if variance_rank[k] < 0][:args.top_n]

    patch = []
    for seg, coh in top:
        for m in months:
            subset = [r for r in rows if r['Segment'] == seg and r['Cohort'] == coh and r['MonthStr'] == m]
            open_row = [r for r in subset if r['Metric'] == 'OpeningGBV'][0]
            coll_row = [r for r in subset if r['Metric'] == 'Coll_Principal'][0]
            target_rate = float(coll_row['Actual']) / float(open_row['Forecast'])
            mob = mob_for(coh, m)
            patch.append({
                'Segment': seg,
                'Cohort': coh,
                'Metric': 'Coll_Principal',
                'MOB_Start': mob,
                'MOB_End': mob,
                'Approach': 'Manual',
                'Param1': f'{target_rate:.6f}',
                'Param2': '',
                'Explanation': f'Backtest lock for {m}: target rate from Actual/FcstOpening',
            })

    with open(args.out, 'w', newline='') as f:
        w = csv.DictWriter(
            f,
            fieldnames=['Segment', 'Cohort', 'Metric', 'MOB_Start', 'MOB_End', 'Approach', 'Param1', 'Param2', 'Explanation'],
        )
        w.writeheader()
        w.writerows(patch)

    print(f'Wrote {args.out} with {len(patch)} rows ({len(top)} cohorts x {len(months)} month(s))')
    for seg, coh in top:
        print(f'  {seg} {coh} total variance={variance_rank[(seg,coh)]:,.2f}')


if __name__ == '__main__':
    main()
