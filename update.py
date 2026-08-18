#! /usr/bin/env python3

import datetime
import json
import re
import subprocess
import tomllib
import urllib.request

with open("package.toml", "rb") as file:
    pkgconfig = tomllib.load(file)

if pkgconfig["source"] == "github-release":
    print(f"Checking Github API for {pkgconfig['github_repo']} releases")
    api_endpoint = f"https://api.github.com/repos/{pkgconfig['github_repo']}/releases/latest"
    with urllib.request.urlopen(api_endpoint) as response:
        api_info = json.loads(response.read())

    repo = f"https://github.com/{pkgconfig['github_repo']}"
    tag = True
    build_repo = pkgconfig['github_repo']
    checkout = api_info['tag_name']
elif pkgconfig["source"] == "branch":
    repo = pkgconfig["repo"]
    tag = False
    build_repo = pkgconfig['github_repo']
    checkout = pkgconfig["branch"]

if tag:
    print(f"Checking commit for tag {checkout} on repo {repo}")
    gitCmd = [ "git", "ls-remote", "--exit-code", "--tags", repo, f"refs/tags/{checkout}" ]
else:
    print(f"Checking commit for branch {checkout} on repo {repo}")
    gitCmd = [ "git", "ls-remote", "--exit-code", "--branches", repo, f"refs/heads/{checkout}" ]

res = subprocess.run(gitCmd, stdout=subprocess.PIPE, check=True, text=True)
commit = re.split('\\s+', res.stdout)[0]
print(f"Found commit {commit}")

with open(".github/workflows/release.yml", "r+") as file:
    content = file.read()
    reg = re.compile('BUILD_VERSION:\\s+".+"')
    date = datetime.datetime.today().strftime('%Y.%m.%d')
    content = reg.sub(f"BUILD_VERSION: \"{date}\"", content)
    reg = re.compile('BUILD_REPO:\\s+".+"')
    content = reg.sub(f"BUILD_REPO: \"{build_repo}\"", content)
    reg = re.compile('BUILD_COMMIT:\\s+".+"')
    content = reg.sub(f"BUILD_COMMIT: \"{commit}\"", content)
    reg = re.compile('BUILD_CHECKOUT:\\s+".+"')
    content = reg.sub(f"BUILD_CHECKOUT: \"{checkout}\"", content)
    file.seek(0)
    file.write(content)
    file.truncate()
