#!/usr/bin/env python3
"""
Shift down event placements by one for the 2024-25 Regionals entry in
Planning/competitionResults_standardized.txt (NYC NORTH REGIONAL 2024-25).

Effect: For each Team (A/B/C) within that competition block, every event line's
placement becomes the previous event's placement; the first event's placement is removed.

Usage:
  python fix_regionals_shift.py          # dry-run, prints diff preview lines
  python fix_regionals_shift.py --apply  # writes changes in-place
"""

import argparse
import re
from pathlib import Path


PLANNING_PATH = Path('Planning/competitionResults_standardized.txt')
TARGET_HEADERS = ['NYC NORTH REGIONAL 2023-24']


def is_competition_header(line: str) -> bool:
    return bool(re.match(r'^[A-Z\s]+20[0-9]{2}-[0-9]{2}$', line.strip()))


def process(lines: list[str]) -> tuple[list[str], bool]:
    changed = False
    out = lines[:]  # copy

    # Process each target competition
    for target_header in TARGET_HEADERS:
        # Find target competition block boundaries
        start = None
        for i, ln in enumerate(out):
            if ln.strip() == target_header:
                start = i
                break
        if start is None:
            continue

        # End is next competition header or separator line of '='
        end = len(out)
        for j in range(start + 1, len(out)):
            if is_competition_header(out[j].strip()) or out[j].strip().startswith('==='):
                end = j
                break

        # Within [start, end), shift per team
        idx = start
        while idx < end:
            line = out[idx].rstrip('\n')
            if line.strip().startswith('Team ') and line.strip().endswith(' Results:'):
                # Collect event line indices until 'Overall:' or blank or next team/section
                ev_idxs: list[int] = []
                k = idx + 1
                while k < end:
                    s = out[k].rstrip('\n')
                    st = s.strip()
                    if not st:
                        break
                    if st.startswith('Team ') and st.endswith(' Results:'):
                        break
                    if st.startswith('Overall:'):
                        break
                    # Event line looks like 'Event Name: value'
                    if ':' in s:
                        ev_idxs.append(k)
                    k += 1

                if ev_idxs:
                    # Extract event/value pairs
                    events = []
                    for ei in ev_idxs:
                        s = out[ei].rstrip('\n')
                        name, val = s.split(':', 1)
                        events.append((name, val.strip()))

                    # Shift up by one: new[i] = old[i+1]; new[-1] = ''
                    new_vals = [''] * len(events)
                    for ii in range(len(events) - 1):
                        new_vals[ii] = events[ii + 1][1]

                    # Write back
                    for ei, ((name, _old), new_val) in zip(ev_idxs, zip(events, new_vals)):
                        if new_val:
                            out[ei] = f"{name}:{' ' + new_val}\n"
                        else:
                            out[ei] = f"{name}:\n"
                    changed = True
                idx = k
            else:
                idx += 1

    return out, changed


def main() -> None:
    parser = argparse.ArgumentParser(description='Shift up placements for 23-24 Regionals in planning file')
    parser.add_argument('--apply', action='store_true', help='Write changes to file')
    args = parser.parse_args()

    text = PLANNING_PATH.read_text(encoding='utf-8')
    lines = text.splitlines(keepends=True)
    new_lines, changed = process(lines)

    if not changed:
        print('No changes needed (target blocks not found or already adjusted).')
        return

    if args.apply:
        PLANNING_PATH.write_text(''.join(new_lines), encoding='utf-8')
        print('Applied changes to planning file for Regional competition.')
    else:
        print('Dry-run preview (first 40 changed lines shown):')
        diff_count = 0
        for old, new in zip(lines, new_lines):
            if old != new:
                print(f'- {old.rstrip()}')
                print(f'+ {new.rstrip()}')
                diff_count += 1
                if diff_count >= 40:
                    break


if __name__ == '__main__':
    main()


