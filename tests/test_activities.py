"""
Unit tests for activity data and logic.
Tests the structure and behavior of the activities data store.
"""

import pytest


class TestActivityDataInitialization:
    """Tests for activity data initialization."""

    def test_all_nine_activities_exist(self, client):
        """Test that all expected activities are initialized."""
        response = client.get("/activities")
        activities = response.json()

        expected_count = 9
        assert len(activities) == expected_count

    def test_activity_names_are_correct(self, client):
        """Test that activity names match expected values."""
        response = client.get("/activities")
        activities = response.json()

        expected_names = {
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Tennis Club",
            "Art Studio",
            "Drama Club",
            "Debate Team",
            "Science Club"
        }

        assert set(activities.keys()) == expected_names

    def test_all_activities_have_valid_max_participants(self, client):
        """Test that all activities have valid max_participants values."""
        response = client.get("/activities")
        activities = response.json()

        for activity_name, activity_data in activities.items():
            max_participants = activity_data["max_participants"]
            assert max_participants > 0
            assert isinstance(max_participants, int)

    def test_initial_participant_lists_are_valid(self, client):
        """Test that initial participant lists contain only emails."""
        response = client.get("/activities")
        activities = response.json()

        for activity_name, activity_data in activities.items():
            participants = activity_data["participants"]
            assert isinstance(participants, list)
            # All existing participants should be emails
            for participant in participants:
                assert isinstance(participant, str)
                assert "@" in participant


class TestActivityParticipantCountLogic:
    """Tests for participant count logic."""

    def test_participant_count_does_not_exceed_max(self, client):
        """
        Test that participant count doesn't exceed max_participants
        (test the initial state, real enforcement would need max capacity check).
        """
        response = client.get("/activities")
        activities = response.json()

        for activity_name, activity_data in activities.items():
            current = len(activity_data["participants"])
            max_allowed = activity_data["max_participants"]
            assert current <= max_allowed

    def test_no_duplicate_participants_in_activity(self, client):
        """Test that no activity has duplicate participants in initial state."""
        response = client.get("/activities")
        activities = response.json()

        for activity_name, activity_data in activities.items():
            participants = activity_data["participants"]
            # Check for duplicates: if unique count equals list length, no duplicates
            assert len(participants) == len(set(participants))

    def test_description_field_is_non_empty(self, client):
        """Test that all activities have non-empty descriptions."""
        response = client.get("/activities")
        activities = response.json()

        for activity_name, activity_data in activities.items():
            description = activity_data["description"]
            assert len(description) > 0
            assert isinstance(description, str)

    def test_schedule_field_is_non_empty(self, client):
        """Test that all activities have non-empty schedules."""
        response = client.get("/activities")
        activities = response.json()

        for activity_name, activity_data in activities.items():
            schedule = activity_data["schedule"]
            assert len(schedule) > 0
            assert isinstance(schedule, str)


class TestActivityDataConsistency:
    """Tests for data consistency across requests."""

    def test_activities_are_consistent_across_requests(self, client):
        """Test that activity data is consistent across multiple GET requests."""
        response1 = client.get("/activities")
        activities1 = response1.json()

        response2 = client.get("/activities")
        activities2 = response2.json()

        # Both responses should be identical
        assert activities1 == activities2

    def test_activity_names_match_keys(self, client):
        """Test that activity dictionary keys are the activity names."""
        response = client.get("/activities")
        activities = response.json()

        # The keys themselves are the activity names, verify structure
        for activity_name in activities.keys():
            assert isinstance(activity_name, str)
            assert len(activity_name) > 0
