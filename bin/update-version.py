import argparse
import json
from pathlib import Path

def get_args():
    parser = argparse.ArgumentParser(prog='update-version')
    parser.add_argument('-v', '--version', required=True)
    return parser.parse_args()

def main():
    args = get_args()

    repo_path = Path(__file__).parent.parent
    if not repo_path.is_dir():
        raise NotADirectoryError('Could not locate repository.')

    # Update version in JSON file
    with (repo_path / 'version.json').open() as file:
        data = json.load(file)
    data['submitty_version'] = args.version
    with (repo_path / 'version.json').open('w') as file:
        json.dump(data, file, indent=2)

if __name__ == '__main__':
    main()