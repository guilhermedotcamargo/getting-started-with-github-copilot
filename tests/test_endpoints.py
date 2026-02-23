"""
Integration tests for FastAPI endpoints.
Tests all HTTP endpoints for correct behavior, error handling, and edge cases.
"""

import pytest


class TestRootEndpoint:
    """Tests for the root endpoint (GET /)."""

    def test_root_redirect(self, client):
        """Test that root endpoint redirects to static index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"

    def test_root_with_follow_redirect(self, client):
        """Test that following the redirect reaches the static file."""
        response = client.get("/", follow_redirects=True)
        assert response.status_code == 200


class TestGetActivitiesEndpoint:
    """Tests for the GET /activities endpoint."""

    def test_get_all_activities(self, client):
        """Test that get_activities returns all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()

        # Verify all expected activities are present
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Tennis Club",
            "Art Studio",
            "Drama Club",
            "Debate Team",
            "Science Club"
        ]
        assert set(activities.keys()) == set(expected_activities)

    def test_activity_structure(self, client):
        """Test that each activity has the correct structure."""
        response = client.get("/activities")
        activities = response.json()

        required_fields = {"description", "schedule", "max_participants", "participants"}

        for activity_name, activity_data in activities.items():
            assert set(activity_data.keys()) == required_fields
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)

    def test_activity_participants_are_emails(self, client):
        """Test that participants are represented as email strings."""
        response = client.get("/activities")
        activities = response.json()

        for activity_name, activity_data in activities.items():
            for participant in activity_data["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant  # Basic email validation


class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_successful_signup(self, client):
        """Test successful signup for an activity."""
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_signup_increments_participant_count(self, client):
        """Test that signup increments the participant count."""
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Get initial participant count
        response_before = client.get("/activities")
        count_before = len(response_before.json()[activity_name]["participants"])

        # Perform signup
        client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Get updated participant count
        response_after = client.get("/activities")
        count_after = len(response_after.json()[activity_name]["participants"])

        assert count_after == count_before + 1

    def test_signup_duplicate_returns_400(self, client):
        """Test that duplicate signup returns 400 error."""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up

        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_signup_nonexistent_activity_returns_404(self, client):
        """Test that signup for non-existent activity returns 404."""
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_missing_email_param_returns_422(self, client):
        """Test that missing email parameter returns 422 validation error."""
        activity_name = "Chess Club"

        response = client.post(f"/activities/{activity_name}/signup")

        assert response.status_code == 422

    def test_signup_multiple_students_same_activity(self, client):
        """Test that multiple different students can sign up for the same activity."""
        activity_name = "Programming Class"
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"

        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email1}
        )
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email2}
        )

        assert response1.status_code == 200
        assert response2.status_code == 200

        # Verify both are registered
        response_activities = client.get("/activities")
        participants = response_activities.json()[activity_name]["participants"]
        assert email1 in participants
        assert email2 in participants


class TestUnregisterEndpoint:
    """Tests for the POST /activities/{activity_name}/unregister endpoint."""

    def test_successful_unregister(self, client):
        """Test successful unregister from an activity."""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up

        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_unregister_decrements_participant_count(self, client):
        """Test that unregister decrements the participant count."""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Get initial participant count
        response_before = client.get("/activities")
        count_before = len(response_before.json()[activity_name]["participants"])

        # Perform unregister
        client.post(f"/activities/{activity_name}/unregister", params={"email": email})

        # Get updated participant count
        response_after = client.get("/activities")
        count_after = len(response_after.json()[activity_name]["participants"])

        assert count_after == count_before - 1

    def test_unregister_nonexistent_activity_returns_404(self, client):
        """Test that unregister from non-existent activity returns 404."""
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_unregister_not_registered_student_returns_400(self, client):
        """Test that unregistering a student not signed up returns 400."""
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"

        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        assert response.status_code == 400
        assert "not registered" in response.json()["detail"].lower()

    def test_unregister_missing_email_param_returns_422(self, client):
        """Test that missing email parameter returns 422 validation error."""
        activity_name = "Chess Club"

        response = client.post(f"/activities/{activity_name}/unregister")

        assert response.status_code == 422

    def test_signup_then_unregister_workflow(self, client):
        """Test complete signup and unregister workflow."""
        activity_name = "Art Studio"
        email = "artist@mergington.edu"

        # Signup
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200

        # Verify signup
        check_response = client.get("/activities")
        assert email in check_response.json()[activity_name]["participants"]

        # Unregister
        unregister_response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert unregister_response.status_code == 200

        # Verify unregister
        check_response = client.get("/activities")
        assert email not in check_response.json()[activity_name]["participants"]
