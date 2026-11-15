"""Colombia-only Hyper publisher, including local scraper plugins."""
import asyncio
import copy
import os
import re

from colombia_gbfs.registry import activate


def build_config(records):
    # Import after activation, so Hyper sees our filtered discovery function.
    from citybikes.hyper.config import Config
    from citybikes.hyper.publisher import DEFAULTS

    defaults = copy.deepcopy(DEFAULTS)
    interval = int(os.getenv("UPDATE_INTERVAL_SECONDS", "180"))
    if interval < 30:
        raise ValueError("UPDATE_INTERVAL_SECONDS must be at least 30")
    defaults["interval"] = interval
    defaults["enabled"] = False
    defaults["scraper"]["requests_timeout"] = 15
    # Config evaluates patterns in order: disabled globally, selected enabled.
    policies = {r".*": {"enabled": False}}
    for _, _, instance in records:
        policies[r".*::" + re.escape(instance["tag"]) + r"$"] = {"enabled": True}
    return {"schedule": Config(defaults, policies), "queues": [("default", 4)]}


def main():
    records = activate()
    # Do not import the publisher before activate()!
    from citybikes.hyper.publisher import run

    asyncio.run(run(build_config(records)))


if __name__ == "__main__":
    main()
