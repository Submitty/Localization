import json
import subprocess

pr_json = "gh pr list --author \"SubmittyBot\" --json number"
string = subprocess.check_output(pr_json, shell=True, text=True)

output = json.loads(string)

if len(output) > 0:
    output.remove(output[0])

for id in output:
    subprocess.run(['gh', 'pr', 'close', str(id["number"])])
    