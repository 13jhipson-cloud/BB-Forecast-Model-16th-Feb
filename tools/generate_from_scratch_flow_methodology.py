#!/usr/bin/env python3
"""Generate a from-scratch methodology for flow metrics affecting ClosingGBV.

Outputs cohort-specific rules for:
- Coll_Principal
- Coll_Interest
- InterestRevenue

Design intent:
- use StaticCohortAvg by regime windows (1-12, 13-36, 37+)
- for newest cohorts (202508/202509), use a same-segment donor for MOB 1-6,
  then transition back to StaticCohortAvg.
"""
import argparse
import csv
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

NS = {
    'a': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
    'p': 'http://schemas.openxmlformats.org/package/2006/relationships',
}

DONOR_MAP = {
    'NON PRIME': '202507',
    'NRP-S': '202507',
    'NRP-M': '202507',
    'NRP-L': '202507',
    'PRIME': '202507',
}

FLOW_METRICS = ['Coll_Principal', 'Coll_Interest', 'InterestRevenue']


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


def get_segment_cohort_universe(xlsx_path, month='2025-10'):
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
    combos = set()

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
        m = (base + timedelta(days=int(float(rec['Month'])))).strftime('%Y-%m')
        if m == month and rec.get('Metric') == 'OpeningGBV':
            combos.add((rec['Segment'], rec['Cohort']))

    return sorted(combos)


def rules_for_metric(segment, cohort, metric):
    cohort_int = int(cohort)
    rows = []

    # Very recent cohorts: use same-segment donor briefly, then static actual-only averages
    if cohort_int >= 202508:
        donor = DONOR_MAP[segment]
        rows.append((1, 6, 'DonorCohort', donor, '', f'Recent cohort bridge via same-segment donor {donor}'))
        rows.append((7, 24, 'StaticCohortAvg', '3', '', 'Post-bridge stabilisation using actual-only history'))
        rows.append((25, 999, 'StaticCohortAvg', '6', '', 'Mature stabilisation using actual-only history'))
        return rows

    # Default regime structure
    rows.append((1, 12, 'StaticCohortAvg', '3', '', 'Early regime using recent actual-only cohort points'))
    rows.append((13, 36, 'StaticCohortAvg', '6', '', 'Mid regime using actual-only cohort points'))
    rows.append((37, 999, 'StaticCohortAvg', '12', '', 'Late regime tail cap using actual-only cohort points'))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--xlsx', default='BB Forecast V5.2.xlsx')
    ap.add_argument('--month', default='2025-10')
    ap.add_argument('--out', default='Rate_Methodology_from_scratch_flow_metrics.csv')
    args = ap.parse_args()

    universe = get_segment_cohort_universe(args.xlsx, month=args.month)

    out_rows = []
    for segment, cohort in universe:
        for metric in FLOW_METRICS:
            for mob_start, mob_end, approach, p1, p2, expl in rules_for_metric(segment, cohort, metric):
                out_rows.append({
                    'Segment': segment,
                    'Cohort': cohort,
                    'Metric': metric,
                    'MOB_Start': mob_start,
                    'MOB_End': mob_end,
                    'Approach': approach,
                    'Param1': p1,
                    'Param2': p2,
                    'Explanation': expl,
                })

    with open(args.out, 'w', newline='') as f:
        w = csv.DictWriter(
            f,
            fieldnames=['Segment', 'Cohort', 'Metric', 'MOB_Start', 'MOB_End', 'Approach', 'Param1', 'Param2', 'Explanation'],
        )
        w.writeheader()
        w.writerows(out_rows)

    print(f'Wrote {args.out} with {len(out_rows)} rows from {len(universe)} segment×cohort combinations')


if __name__ == '__main__':
    main()
