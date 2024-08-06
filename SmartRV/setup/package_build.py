import os
from pyexpat import version_info
import sys
import shutil
import json
import argparse
import datetime

from update_version import  get_versions, update_yml
from convert_md import update_version_in_md_file, convert_md_to_html

# Check params
# Check or create target folder

BASE_PATH = os.path.join(
    os.path.split(
        os.path.abspath(sys.argv[0])
    )[0],
    '../'
)

# Update the about.html using about.md
from_dir = BASE_PATH

new_v = get_versions(from_dir)
#
file_path = os.path.join(BASE_PATH, 'data/about.md')

update_version_in_md_file(file_path, new_v['version'])

html_content = convert_md_to_html(file_path)
print(html_content)
print("PK 1")

DEPLOY_LIST = [
    'main_service',
    'iot_service',
    'can_service',
    'system_service',
    'kiosk_config',
    'bt_service',
    "update_service",
    'common_libs',
    'requirements.txt',
    'version.json',
    'data',
    'hmi_tools',
    # 'setup/pyPackages/pypackages.tgz',
]

parser = argparse.ArgumentParser()
parser.add_argument("target", help="target directory")
parser.add_argument("--existing-version", help="use existing version number", action="store_true")

args = parser.parse_args()

this = sys.argv[0]
target = args.target

print("PK 2")
print(this, target)
print(os.path.abspath(this), os.path.abspath(target))

if os.path.exists(target):
    #delete = input(f'Delete {target}: [y|n]')
    delete = 'y'
    if delete.lower() == 'y':
        shutil.rmtree(target)
        # os.makedirs(target)
    else:
        sys.exit(1)

print("PK 3")
# else:
    # os.makedirs(target)

try:
    version_data = json.load(open('../version.json', 'r'))
except IOError as err:
    print(f' Error {err}')
    version_data = {}

version_input = version_data.get('version')

if not args.existing_version:
    print("PK 3a")
    version_input = input(f'Version [{version_data.get("version")}]')

if not version_input:
    print("PK 3b")
    version_input = version_data.get('version')

print("PK 4")
version = {
    'version': version_input,
    'date': str(datetime.datetime.utcnow()),
    'modules': {
        'main_service': None,
        #'hal': None,
        'can_service': None,
        'iot_service': None,
        'system_service': None
    }
}

json.dump(version, open('../version.json', 'w'), indent=4)


# ADD yml update

print("PK 7")
from_dir = ".."

new_v = get_versions(from_dir)

to_dir = os.path.join(from_dir, 'Pipelines', 'variables')
update_yml(to_dir, new_v)

print(f'Versions found: {new_v}')
rel_version = new_v['version']
print(f'Release found: {rel_version}')

with open('../data/about.html', 'w') as out_file:
    out_file.write(html_content)

print("Updated about.html")
for path in DEPLOY_LIST:
    source_path = os.path.join(BASE_PATH, path)
    destination_path = os.path.join(target, path)

    print(f"PK {path}")

    if '/' in path:
        os.makedirs(os.path.split(destination_path)[0])

    print(source_path, destination_path)
    if os.path.isdir(source_path):
        # if not os.path.exists(destination_path):
        #     os.makedirs(destination_path)

        shutil.copytree(source_path, destination_path)
    else:
        try:
            shutil.copy(source_path, destination_path)
        except FileNotFoundError as err:
            if 'pypackages' in source_path:
                # Allow to skip this for pipeline
                # TODO: Find a better way to pull the dependencies as a separate failable step
                continue
            else:
                raise
