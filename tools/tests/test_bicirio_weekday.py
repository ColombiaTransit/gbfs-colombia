"""Offline unit tests; they never contact BiciRio."""
import unittest
from tools.check_bicirio_weekday import (
    BIKES, STATIONS, as_records, clean_bicycle_state, coordinate_status, exit_status, run_check, select_stations
)


class TestBiciRioWeekday(unittest.TestCase):
    def setUp(self):
        self.stations = [
            {"id": 37, "name": "Palos Verdes", "state": "Open",
             "stationType": "TYPE_2", "latitude": -75.38391,
             "longitude": 6.126118, "connectionState": False},
            {"id": 21, "name": "El Faro", "state": "Open",
             "stationType": "TYPE_2", "latitude": 6.147648,
             "longitude": -75.39029, "connectionState": True},
            {"id": 40, "name": "Virtual", "state": "Open",
             "stationType": "TYPE_3", "latitude": 0.0, "longitude": 0.0},
            {"id": 38, "name": "Bodega", "state": "Open",
             "stationType": "TYPE_2", "latitude": -75.3,
             "longitude": 6.1},
            {"id": 30, "name": "Closed", "state": "Closed",
             "stationType": "TYPE_2", "latitude": -75.4,
             "longitude": 6.12},
        ]

    def test_geographic_orientation(self):
        self.assertEqual(coordinate_status(self.stations[0]), "swapped")
        self.assertEqual(coordinate_status(self.stations[1]), "correct")
        self.assertEqual(coordinate_status(self.stations[2]), "invalid_or_unknown")

    def test_filters_invalid_or_closed_stations(self):
        self.assertEqual([st["id"] for st in select_stations(self.stations)],
                         [21, 37])

    def test_payload_parsing(self):
        self.assertEqual(as_records({"data": [1, 2]}), [1, 2])
        with self.assertRaises(ValueError):
            as_records({"success": True})

    def test_nonempty_response_and_no_bicycle_ids_leaked(self):
        called = []

        def fake_fetch(url):
            called.append(url)
            if url == STATIONS:
                return self.stations, False
            if url == BIKES + "21":
                return [], False
            if url == BIKES + "37":
                return [{"id": "do-not-publish-vehicle-id", "bicycleState": "AVAILABLE"}], False
            raise AssertionError(url)

        report = run_check(fetch=fake_fetch, pause=lambda _: None)
        self.assertEqual(report["result"], "nonempty_bicycle_responses")
        self.assertEqual(report["total_bicycle_records"], 1)
        self.assertEqual(report["bicycle_state_counts"], {"AVAILABLE": 1})
        self.assertEqual(report["tested_stations"][1]["bicycle_state_counts"], {"AVAILABLE": 1})
        self.assertEqual(report["stations_with_nonempty_bicycle_response"], 1)
        self.assertFalse(report["tls_verified_for_all_requests"])
        self.assertNotIn("do-not-publish-vehicle-id", str(report))
        self.assertEqual(called, [STATIONS, BIKES + "21", BIKES + "37"])

    def test_bicycle_state_category_sanitizer(self):
        self.assertEqual(clean_bicycle_state("AVAILABLE"), "AVAILABLE")
        self.assertEqual(clean_bicycle_state("On_Maintenance"), "On_Maintenance")
        self.assertEqual(clean_bicycle_state(3), "3")
        self.assertEqual(clean_bicycle_state("secret token; unauthorized"), "<unknown_or_missing>")
        self.assertEqual(clean_bicycle_state({"id": "private"}), "<unknown_or_missing>")
        self.assertEqual(clean_bicycle_state(None), "<unknown_or_missing>")

    def test_state_aggregate_does_not_persist_bicycle_identifiers(self):
        def fetch(url):
            if url == STATIONS:
                return self.stations, True
            if url == BIKES + "21":
                return [{"id": "secret-id-1", "serial": "private-serial",
                         "bicycleState": "AVAILABLE"},
                        {"id": "secret-id-2", "bicycleState": "MAINTENANCE"}], True
            return [], True

        report = run_check(fetch=fetch, pause=lambda _: None)
        self.assertEqual(report["bicycle_state_counts"], {"AVAILABLE": 1, "MAINTENANCE": 1})
        self.assertNotIn("secret-id", str(report))
        self.assertNotIn("private-serial", str(report))

    def test_empty_responses_not_accepted_as_proof_of_availability(self):
        def fake_fetch(url):
            return (self.stations if url == STATIONS else []), True

        report = run_check(fetch=fake_fetch, pause=lambda _: None)
        self.assertEqual(report["result"], "no_nonempty_bicycle_responses")
        self.assertEqual(report["total_bicycle_records"], 0)
        self.assertEqual(exit_status(report), 0)

    def test_actual_api_failure_is_a_failure(self):
        def fake_fetch(url):
            if url == STATIONS:
                return self.stations, True
            raise OSError("Simulated upstream HTTP failure")

        report = run_check(fetch=fake_fetch, pause=lambda _: None)
        self.assertEqual(report["result"], "bicycle_api_errors")
        self.assertEqual(exit_status(report), 1)

    def test_station_api_error_is_a_failure(self):
        def fake_fetch(url):
            raise OSError("Simulated station API failure")

        report = run_check(fetch=fake_fetch, pause=lambda _: None)
        self.assertEqual(report["result"], "station_api_error")
        self.assertEqual(exit_status(report), 1)


if __name__ == "__main__":
    unittest.main()
