import json
import re
from argparse import ArgumentParser, Namespace
from collections import OrderedDict
from pathlib import Path


def get_args() -> Namespace:
    parser = ArgumentParser(prog='update-version')
    parser.add_argument('-v', '--version', required=True)
    return parser.parse_args()


def get_template_data() -> dict:
    pattern = re.compile(r"localize\s*?\(\s*?(?P<q1>[\'\"])(?P<key>[\w\.]+?)\s*?(?P=q1)"
                         r",\s*?(?P<q2>[\'\"])(?P<val>.+?)(?<!\\\\)(?P=q2)\s*?.*?\)")

    template_path = Path(__file__).parent.parent.parent / 'Submitty' / 'site' / 'app' / 'templates'
    if not template_path.is_dir():
        raise NotADirectoryError('Could not locate template directory.')

    data = dict()

    # Loop through template files
    for child in template_path.iterdir():
        if not child.is_file() or child.suffix != '.twig':
            continue

        # Split into template blocks {{ }}
        body = child.read_text()
        parts = [part.split('}}')[0] for part in body.split('{{')[1:]]

        for part in parts:
            for match in re.finditer(pattern, part):
                group = match.groupdict()
                tree = group.get('key').split('.')
                val = group.get('val')

                last_key = tree.pop()

                loc = data  # Current location in tree (should always be dict)
                for key in tree:
                    if key in loc:
                        loc = loc[key]
                        if not isinstance(loc, dict):
                            raise KeyError('Duplicate template key found: ' + key)
                    else:
                        loc[key] = dict()
                        loc = loc[key]

                if not isinstance(loc, dict):
                    raise KeyError('Duplicate template key found: ' + key)
                loc[last_key] = val

    return data


def update_data(original: OrderedDict, updated: dict) -> OrderedDict:
    result = OrderedDict()

    # Update existing keys
    for key, val in original.items():
        if key not in updated:
            continue

        if isinstance(val, OrderedDict) and isinstance(updated[key], dict):
            result[key] = update_data(val, updated[key])
        else:
            result[key] = updated[key]

    # Add new keys
    for key, val in updated.items():
        if key not in original:
            if isinstance(val, dict):
                result[key] = OrderedDict(val)
            else:
                result[key] = val

    return result


def main():
    args = get_args()

    repo_path = Path(__file__).parent.parent
    if not repo_path.is_dir():
        raise NotADirectoryError('Could not locate repository.')

    # Update version in JSON file
    with (repo_path / 'config.json').open() as file:
        data = json.load(file, object_pairs_hook=OrderedDict)
    data['submitty_version'] = args.version
    with (repo_path / 'config.json').open('w') as file:
        json.dump(data, file, indent=2)

    # Update default lang data
    with (repo_path / 'lang' / 'en_US.json').open() as file:
        json_data = json.load(file, object_pairs_hook=OrderedDict)
    json_data = update_data(json_data, get_template_data())
    with (repo_path / 'lang' / 'en_US.json').open('w') as file:
        json.dump(json_data, file, indent=4)


if __name__ == '__main__':
    main()
