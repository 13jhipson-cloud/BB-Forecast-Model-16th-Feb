#!/usr/bin/env python3
"""Generate segment-level Coll_Principal multiplier overlays from workbook backtest.

Method:
- Read `14_Backtest_Comparison` rows where Metric == Coll_Principal
- Restrict to requested month window (default: 2025-10 .. 2026-01)
- For each segment, compute ratio = Actual / Forecast (sums)
- Emit overlay rows: Multiply Coll_Principal by ratio for each segment
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


def read_rows(zf, sheet_path, shared):
    root = ET.fromstring(zf.read(sheet_path))
    rows = []
    for row in root.findall('.//a:sheetData/a:row', NS):
        vals = {}
        for c in row.findall('a:c', NS):
            ref = c.attrib.get('r', '')
            col = ''.join(ch for ch in ref if ch.isalpha())
            t = c.attrib.get('t')
            v = c.find('a:v', NS)
            if v is None:
                continue
            x = v.text
            if t == 's':
                x = shared[int(x)]
            vals[col] = x
        if vals:
            rows.append(vals)
    return rows


def excel_serial_to_month(serial_str):
    base = datetime(1899, 12, 30)
    dt = base + timedelta(days=int(float(serial_str)))
    return dt.strftime('%Y-%m')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--xlsx', default='BB Forecast V5.2.xlsx')
    ap.add_argument('--month-start', default='2025-10')
    ap.add_argument('--month-end', default='2026-01')
    ap.add_argument('--out', default='sample_data/Overlays.csv')
    args = ap.parse_args()

    with zipfile.ZipFile(args.xlsx) as zf:
        shared = load_shared_strings(zf)
        spath = sheet_path_by_name(zf, '14_Backtest_Comparison')
        rows = read_rows(zf, spath, shared)

    header = [rows[0].get(c, '') for c in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']]
    data = [dict(zip(header, [r.get(c, '') for c in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']])) for r in rows[1:]]

    sums = defaultdict(lambda: {'Forecast': 0.0, 'Actual': 0.0})

    for r in data:
        if r.get('Metric') != 'Coll_Principal':
            continue
        m = excel_serial_to_month(r['Month'])
        if not (args.month_start <= m <= args.month_end):
            continue
        seg = r['Segment']
        sums[seg]['Forecast'] += float(r['Forecast'])
        sums[seg]['Actual'] += float(r['Actual'])

    out_rows = []
    for seg in sorted(sums):
        f = sums[seg]['Forecast']
        a = sums[seg]['Actual']
        ratio = (a / f) if f else 1.0
        out_rows.append({
            'Segment': seg,
            'ForecastMonth_Start': f'{args.month_start}-01',
            'ForecastMonth_End': '',
            'Metric': 'Coll_Principal',
            'Type': 'Multiply',
            'Value': f'{ratio:.6f}',
            'Explanation': f'Calibrated from {args.month_start}..{args.month_end} backtest Actual/Forecast ratio',
        })

    with open(args.out, 'w', newline='') as f:
        writer = csv.DictWriter(
            f,
            fieldnames=['Segment', 'ForecastMonth_Start', 'ForecastMonth_End', 'Metric', 'Type', 'Value', 'Explanation'],
        )
        writer.writeheader()
        writer.writerows(out_rows)

    print(f'Wrote {args.out} with {len(out_rows)} segment multipliers')
    for seg in sorted(sums):
        f = sums[seg]['Forecast']
        a = sums[seg]['Actual']
        ratio = (a / f) if f else 1.0
        print(f'  {seg:10s} Forecast={f:,.0f} Actual={a:,.0f} Ratio={ratio:.4f}')


if __name__ == '__main__':
    main()
