"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestActivitiesEndpoint:
    """Tests for the /activities endpoint"""
    
    def test_get_activities_returns_200(self):
        """Test that GET /activities returns status 200"""
        response = client.get("/activities")
        assert response.status_code == 200
    
    def test_get_activities_returns_json(self):
        """Test that GET /activities returns valid JSON"""
        response = client.get("/activities")
        data = response.json()
        assert isinstance(data, dict)
    
    def test_get_activities_contains_expected_fields(self):
        """Test that each activity contains required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
    
    def test_get_activities_has_sample_data(self):
        """Test that activities list has sample data"""
        response = client.get("/activities")
        activities = response.json()
        assert len(activities) > 0
        assert "Chess Club" in activities
        assert "Programming Class" in activities


class TestSignupEndpoint:
    """Tests for the /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant(self):
        """Test signing up a new participant"""
        email = "test.user@mergington.edu"
        activity = "Chess Club"
        
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity in data["message"]
    
    def test_signup_duplicate_participant_fails(self):
        """Test that signing up the same participant twice fails"""
        email = "duplicate@mergington.edu"
        activity = "Programming Class"
        
        # First signup should succeed
        response1 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Second signup with same email should fail
        response2 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]
    
    def test_signup_nonexistent_activity_fails(self):
        """Test that signing up for non-existent activity fails"""
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_signup_updates_participant_list(self):
        """Test that signup actually adds participant to list"""
        email = "new.participant@mergington.edu"
        activity = "Gym Class"
        
        # Get initial participant count
        response_before = client.get("/activities")
        participants_before = response_before.json()[activity]["participants"]
        initial_count = len(participants_before)
        
        # Sign up new participant
        client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Get updated participant count
        response_after = client.get("/activities")
        participants_after = response_after.json()[activity]["participants"]
        final_count = len(participants_after)
        
        assert final_count == initial_count + 1
        assert email in participants_after


class TestRemoveEndpoint:
    """Tests for the /activities/{activity_name}/remove endpoint"""
    
    def test_remove_existing_participant(self):
        """Test removing an existing participant"""
        email = "remove.me@mergington.edu"
        activity = "Soccer Team"
        
        # First, sign up the participant
        client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Then remove them
        response = client.post(
            f"/activities/{activity}/remove",
            params={"email": email}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert "Removed" in data["message"]
    
    def test_remove_nonexistent_participant_fails(self):
        """Test that removing non-existent participant fails"""
        response = client.post(
            "/activities/Basketball Club/remove",
            params={"email": "notexist@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_remove_from_nonexistent_activity_fails(self):
        """Test that removing from non-existent activity fails"""
        response = client.post(
            "/activities/Nonexistent Club/remove",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_remove_updates_participant_list(self):
        """Test that remove actually removes participant from list"""
        email = "temp.participant@mergington.edu"
        activity = "Art Club"
        
        # Sign up participant
        client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Get participant count before removal
        response_before = client.get("/activities")
        count_before = len(response_before.json()[activity]["participants"])
        
        # Remove participant
        client.post(
            f"/activities/{activity}/remove",
            params={"email": email}
        )
        
        # Get participant count after removal
        response_after = client.get("/activities")
        count_after = len(response_after.json()[activity]["participants"])
        assert email not in response_after.json()[activity]["participants"]
        
        assert count_after == count_before - 1


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static(self):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code in [301, 302, 307, 308]
        assert "static" in response.headers.get("location", "").lower()
