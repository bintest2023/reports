from __future__ import annotations
import typing as t
import sys
from pathlib import Path
import json
import dataclasses

Table: t.TypeAlias = 'list[list[str]]'

@dataclasses.dataclass
class TestCaseResult:
    total_tests: int = 0
    failed_tests: int = 0
    seconds: float = float('nan')
    result: bool = False


def save_table(tbl: Table, file: Path) -> None:
    with file.open('wt', encoding='utf-8') as f:
        write_row = lambda l: f.write('| ' + ' | '.join(l) + ' |\n')

        write_row(tbl[0])
        write_row(['---'] * len(tbl[0]))
        for line in tbl[1:]:
            write_row(line)


def read_data(path: Path) -> dict[str, dict[str, dict[str, TestCaseResult]]]:
    data = {}
    for file in path.rglob('*.json'):
        try:
            content = json.load(file.open('rt', encoding='utf-8'))
            content = {k: v for k, v in content.items() if k and v is not None}
            content = {k: TestCaseResult(**v) for k, v in content.items()}
        except Exception:
            import traceback

            print(f'Unable to parse {file}:', file=sys.stderr)
            traceback.print_exc()
            continue

        username = file.parent.name
        test = file.stem
        data.setdefault(username, {})[test] = content
    return data


def make_test_table(test: str) -> Table:
    result = []
    result.append(['username'] + [*test2subcases[test]])
    for username, user in data.items():
        result.append(row := [username])
        for subcase in test2subcases[test]:
            tcres = data[username].get(test, {}).get(subcase, None)
            if tcres is None:
                row.append('-')
            elif tcres.result:
                row.append('OK')
            else:
                row.append(f'{tcres.total_tests - tcres.failed_tests}/{tcres.total_tests}')
    return result


def make_global_table() -> Table:
    result = []
    result.append(['username'] + [*tests])
    for username, user in data.items():
        result.append(row := [username])
        for test in tests:
            if test not in user:
                row.append('-')
                continue

            subcases = test2subcases[test]
            cnt = sum(subcase in user[test] and user[test][subcase].result for subcase in subcases)
            if cnt == len(subcases):
                row.append('OK')
            else:
                row.append(f'{cnt}/{len(subcases)}')
    return result


data_dir = Path() / 'users'
tables_dir = Path() / 'results'

# username->testname->subcasename->result
data = read_data(data_dir)
tests = sorted(set(test for user in data.values() for test in user))
test2subcases = {
    test: sorted(set(subcase for user in data.values() for subcase in user.get(test, {})))
    for test in tests
}



def main() -> None:
    save_table(make_global_table(), tables_dir / 'main.md')
    for test in tests:
        save_table(make_test_table(test), tables_dir / f'{test}.md')


if __name__ == '__main__':
    main()
