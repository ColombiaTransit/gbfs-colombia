"""Example only: copy this file and implement update() for a real system.

This adapter is not enabled or registered by default.
"""
from pybikes.base import BikeShareSystem, BikeShareStation


class ExampleAdapter(BikeShareSystem):
    sync = True

    def update(self, scraper=None):
        # Replace this with an authorized provider API or page parser.
        # Use BikeShareStation(name=..., latitude=..., longitude=...,
        #                      bikes=..., free=..., extra={"uid": "..."})
        # and assign the resulting list to self.stations.
        #
        # Keep IDs stable and never fabricate availability information.
        raise NotImplementedError("Implement the real upstream data source")
