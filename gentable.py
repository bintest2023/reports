from __future__ import annotations
import typing as t
import json
from pathlib import Path
import sys
import dataclasses

data_dir = Path() / 'users'
tables_dir = Path() / 'results'

@dataclasses.dataclass
class TestCaseResult:
    total_tests: int = 0
    failed_tests: int = 0
    seconds: float = float('nan')
    result: bool = False

def save_table(tbl: list[list[str]], file: Path) -> None:
    print(f'Saving tbl to {file}...')
    pprint(tbl)
    print()
    with file.open('wt', encoding='utf-8') as f:
        f.write(f'| ')
        f.write(' | '.join(tbl[0]))
        f.write(f' |\n')

        f.write(f'| ')
        f.write(' | '.join(['---'] * len(tbl[0])))
        f.write(f' |\n')

        for line in tbl[1:]:
            f.write(f'| ')
            f.write(' | '.join(line))
            f.write(f' |\n')



data: dict[str, dict[str, dict[str, TestCaseResult]]] = {}
# {'denball': {'arrayd': {'a': TestCaseResult, 'b': TestCaseResult}}}

for file in data_dir.rglob('*.json'):
    user = file.parent.name
    test = file.stem
    try:
        content = json.load(file.open('rt', encoding='utf-8'))
        content = {k: v for k, v in content.items() if k and v is not None}
        content = {k: TestCaseResult(**v) for k, v in content.items()}
    except Exception:
        import traceback
        print(f'Unable to parse {file}:', file=sys.stderr)
        traceback.print_exc()
        continue

    if user not in data:
        data[user] = {}

    data[user][test] = content


test_suites = set(name for user in data.values() for name in user)

# per-test tables
for test in test_suites:
    subcases = sorted(set(subcase for user in data.values() for subcase in user.get(test, {})))

    result: list[list[str]] = []
    result.append(['Username'] + [*subcases])
    for username, user in data.items():
        row = [username]
        result.append(row)
        for subcase in subcases:
            tcres = data[username].get(test, {}).get(subcase, None)
            if tcres is None:
                row.append('-')
            elif tcres.result:
                row.append('OK')
            else:
                row.append(f'{tcres.total_tests - tcres.failed_tests}/{tcres.total_tests}')
    save_table(result, tables_dir / f'{test}.md')

# global table
result: list[list[str]] = []
result.append(['Username'] + [*test_suites])
for username, user in data.items():
    row = [username]
    result.append(row)
    for test in test_suites:
        subcases = sorted(set(subcase for user in data.values() for subcase in user.get(test, {})))
        cnt = 0
        if test not in user:
            row.append('-')
            continue

        for subcase in subcases:
            if subcase not in user[test]:
                continue
            if not user[test][subcase].result:
                continue
            cnt += 1

        if cnt == len(subcases):
            row.append('OK')
        else:
            row.append(f'{cnt}/{len(subcases)}')




save_table(result, tables_dir / f'main.md')
