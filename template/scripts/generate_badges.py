#!/usr/bin/env python3
import os

import anybadge
import yaml


badges = []
bool_options = {
    "Uses database": "include_database",
    "Uses redis": "include_redis",
    "Uses NATS": "use_nats",
    "Uses Resgate": "use_resgate",
}


def _yes_no(value: bool) -> str:
    return "Yes" if value else "No"


def _red_green(value: bool) -> str:
    return "green" if value else "red"


def _main() -> None:
    with open(".copier-answers.yml") as file:
        ca = yaml.safe_load(file)

        badges.append(anybadge.Badge("Template type", "Python", default_color="teal"))
        badges.append(anybadge.Badge("Template version", ca["_commit"], default_color="teal"))

        for label, key in bool_options.items():
            val = ca.get(key, False)
            badges.append(anybadge.Badge(label, _yes_no(val), default_color=_red_green(val)))

    if os.path.isfile("helm/Chart.yaml"):
        with open("helm/Chart.yaml") as file:
            helm = yaml.safe_load(file)
            holodeck = [dep for dep in helm.get("dependencies", []) if dep["name"] == "holodeck-service"]
            if holodeck:
                version = holodeck[0].get("version")
                if version:
                    badges.append(anybadge.Badge("Helm", version, default_color="orange"))

    if not os.path.exists("scripts/badges"):
        os.makedirs("scripts/badges")

    for badge in badges:
        badge.write_badge(f"scripts/badges/{badge.label.lower().replace(' ', '_')}.svg", overwrite=True)


if __name__ == "__main__":
    _main()
