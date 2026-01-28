"""Tests for the Mergington High School API"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

client = TestClient(app)


class TestActivitiesEndpoint:
    """Tests for the /activities endpoint"""

    def test_get_activities_returns_200(self):
        """Test that GET /activities returns 200 status code"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self):
        """Test that GET /activities returns a dictionary"""
        response = client.get("/activities")
        data = response.json()
        assert isinstance(data, dict)

    def test_get_activities_contains_expected_activities(self):
        """Test that activities list contains expected activities"""
        response = client.get("/activities")
        activities = response.json()
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Basketball Team" in activities

    def test_activity_has_required_fields(self):
        """Test that each activity has all required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupEndpoint:
    """Tests for the /activities/{activity_name}/signup endpoint"""

    def test_signup_with_valid_activity_returns_200(self):
        """Test signing up for a valid activity returns 200"""
        response = client.post(
            "/activities/Chess Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200

    def test_signup_returns_success_message(self):
        """Test that signup returns a success message"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        data = response.json()
        assert "message" in data
        assert "Signed up" in data["message"]

    def test_signup_with_invalid_activity_returns_404(self):
        """Test signing up for non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_adds_participant_to_activity(self):
        """Test that signup actually adds the participant to the activity"""
        email = "participant-test@mergington.edu"
        
        # Get initial participants count
        response_before = client.get("/activities")
        participants_before = response_before.json()["Programming Class"]["participants"]
        initial_count = len(participants_before)
        
        # Sign up
        response = client.post(
            "/activities/Programming Class/signup?email=" + email
        )
        assert response.status_code == 200
        
        # Verify participant was added
        response_after = client.get("/activities")
        participants_after = response_after.json()["Programming Class"]["participants"]
        assert email in participants_after
        assert len(participants_after) == initial_count + 1


class TestUnregisterEndpoint:
    """Tests for the /activities/{activity_name}/unregister endpoint"""

    def test_unregister_with_valid_participant_returns_200(self):
        """Test unregistering a valid participant returns 200"""
        # First sign up
        email = "todelete@mergington.edu"
        client.post("/activities/Tennis Club/signup?email=" + email)
        
        # Then unregister
        response = client.post(
            "/activities/Tennis Club/unregister?email=" + email
        )
        assert response.status_code == 200

    def test_unregister_returns_success_message(self):
        """Test that unregister returns a success message"""
        email = "todelete2@mergington.edu"
        client.post("/activities/Art Studio/signup?email=" + email)
        
        response = client.post(
            "/activities/Art Studio/unregister?email=" + email
        )
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]

    def test_unregister_with_invalid_activity_returns_404(self):
        """Test unregistering from non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Club/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404

    def test_unregister_removes_participant(self):
        """Test that unregister actually removes the participant"""
        email = "todelete3@mergington.edu"
        activity = "Drama Club"
        
        # Sign up first
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Verify they're registered
        response = client.get("/activities")
        assert email in response.json()[activity]["participants"]
        
        # Unregister
        client.post(f"/activities/{activity}/unregister?email={email}")
        
        # Verify they're removed
        response = client.get("/activities")
        assert email not in response.json()[activity]["participants"]

    def test_unregister_nonexistent_participant_returns_400(self):
        """Test unregistering a participant who's not signed up returns 400"""
        response = client.post(
            "/activities/Science Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not found" in response.json()["detail"]


class TestRootEndpoint:
    """Tests for the root endpoint"""

    def test_root_redirects_to_static(self):
        """Test that root endpoint redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
