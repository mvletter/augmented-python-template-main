#!/usr/bin/env python3
import os
import random
import sys
from argparse import ArgumentParser
from pathlib import PosixPath

import requests
from codeowners import CodeOwners, OwnerTuple


namespace = os.environ.get("CI_PROJECT_PATH")
assert namespace, "Missing env var 'CI_PROJECT_PATH'"

if __name__ == "__main__":
    parser = ArgumentParser(prog=__name__)
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--random-username", action="store_true")
    parser.add_argument("--username-to-id", type=str)
    options = parser.parse_args(args=sys.argv[1:])

    REPOOWNERS_FILE = str(PosixPath(__file__).parent / "REPOOWNERS")
    with open(REPOOWNERS_FILE) as f:
        # REPOOWNERS uses the codeowner syntax to match repository paths to users.
        owners = CodeOwners(f.read())

    if options.verify:
        if not namespace.startswith("holodeck/templates"):
            # Verify repository can be found in repoowners. (CI_PROJECT_PATH)
            names: list[OwnerTuple] = owners.of(f"{namespace}")
            assert names != [], f"{namespace!r} is not yet represented in {REPOOWNERS_FILE}"

        # Verify all usernames can be found in gitlab.
        all_usernames = set()
        for regex, path, *rest in owners.paths:
            for usertype, username in owners.of(path):
                if usertype == "USERNAME":
                    all_usernames.add(username.removeprefix("@"))

        base_url = os.environ.get("CI_API_V4_URL")
        path = "/users"
        for username in all_usernames:
            response = requests.get(
                f"{base_url}{path}",
                headers={"PRIVATE-TOKEN": os.environ.get("TEMPLATE_UPDATE_GIT_TOKEN")},
                params={"search": username},
                timeout=(5, 30),
            )
            results = response.json()
            assert len(results) > 0, f"No users found matching '{username}'"
            if len(results) > 1:
                import json

                print(json.dumps(results, indent=4))
                filtered_results = [result for result in results if result["username"] == username]
                assert len(filtered_results) == 1, f"Too many users found matching '{username}'"
                print(filtered_results[0]["id"])
    elif options.random_username:
        usernames = set()
        for usertype, username in owners.of(f"{namespace}"):
            if usertype == "USERNAME":
                usernames.add(username.removeprefix("@"))
        random_username = random.choice(list(usernames))  # nosec B311
        print(random_username)
    elif username := options.username_to_id:
        base_url = os.environ.get("CI_API_V4_URL")
        path = "/users"
        response = requests.get(
            f"{base_url}{path}",
            headers={
                "PRIVATE-TOKEN": os.environ.get("TEMPLATE_UPDATE_GIT_TOKEN"),
                "Accept": "application/json",
            },
            params={"search": username},
            timeout=(5, 30),
        )
        results = response.json()
        assert len(results) > 0, f"No users found matching '{username}'"
        if len(results) == 1:
            print(results[0]["id"])
        else:
            filtered_results = [result for result in results if result["username"] == username]
            assert len(filtered_results) == 1, f"Too many users found matching '{username}'"
            print(filtered_results[0]["id"])
    else:
        raise RuntimeError("No options provided, pass -h to see which options are available")
