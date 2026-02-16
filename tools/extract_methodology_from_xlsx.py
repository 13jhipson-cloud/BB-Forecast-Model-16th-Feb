#!/usr/bin/env python3
"""Extract 7_Rate_Methodology_Rules from workbook without pandas/openpyxl."""
import argparse
import csv
import zipfile
import xml.etree.ElementTree as ET

NS = {
    'a': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
    'p': 'http://schemas.openxmlformats.org/package/2006/relationships',
}


def load_shared_strings(zf):
    if 'xl/sharedStrings.xml' not in zf.namelist():
        return []
    root = ET.fromstring(zf.read('xl/sharedStrings.xml'))
    vals = []
    for si in root.findall('a:si', NS):
        vals.append(''.join(t.text or '' for t in si.findall('.//a:t', NS)))
    return vals


def sheet_path_by_name(zf, name):
    wb = ET.fromstring(zf.read('xl/workbook.xml'))
    rels = ET.fromstring(zf.read('xl/_rels/workbook.xml.rels'))
    rmap = {r.attrib['Id']: r.attrib['Target'] for r in rels.findall('p:Relationship', NS)}
    sheets = wb.find('a:sheets', NS)
    for sh in sheets:
        if sh.attrib.get('name') == name:
            rid = sh.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
            return 'xl/' + rmap[rid]
    raise ValueError(f"Sheet not found: {name}")


def extract_sheet_rows(zf, sheet_path, shared):
    root = ET.fromstring(zf.read(sheet_path))
    rows = []
    for row in root.findall('.//a:sheetData/a:row', NS):
        vals = {}
        for c in row.findall('a:c', NS):
            ref = c.attrib.get('r', '')
            col = ''.join(ch for ch in ref if ch.isalpha())
            t = c.attrib.get('t')
            v = c.find('a:v', NS)
            val = ''
            if v is not None:
                val = v.text
                if t == 's':
                    val = shared[int(val)]
            vals[col] = val
        rows.append(vals)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--xlsx', required=True)
    ap.add_argument('--sheet', default='7_Rate_Methodology_Rules')
    ap.add_argument('--out', required=True)
    args = ap.parse_args()

    with zipfile.ZipFile(args.xlsx) as zf:
        shared = load_shared_strings(zf)
        spath = sheet_path_by_name(zf, args.sheet)
        rows = extract_sheet_rows(zf, spath, shared)

    if not rows:
        raise SystemExit('No rows found')

    cols = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
    header = [rows[0].get(c, '') for c in cols]
    data = [[r.get(c, '') for c in cols] for r in rows[1:] if any(r.get(c, '') for c in cols)]

    with open(args.out, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(data)

    print(f'Wrote {args.out} ({len(data)} rows) from {args.sheet}')


if __name__ == '__main__':
    main()
