from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_root_redirect():
    """Test that root path redirects to static index"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"


def test_get_activities():
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    
    # Check structure
    assert isinstance(data, dict)
    assert len(data) > 0
    
    # Check a specific activity exists
    assert "Chess Club" in data
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


def test_signup_success():
    """Test successful signup"""
    email = "teststudent@mergington.edu"
    activity = "Chess Club"
    
    # Initial participant count
    response = client.get("/activities")
    initial_count = len(response.json()[activity]["participants"])
    
    # Signup
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    result = response.json()
    assert f"Signed up {email} for {activity}" in result["message"]
    
    # Verify added
    response = client.get("/activities")
    data = response.json()
    assert email in data[activity]["participants"]
    assert len(data[activity]["participants"]) == initial_count + 1


def test_signup_duplicate():
    """Test signing up twice fails"""
    email = "duplicatetest@mergington.edu"
    activity = "Programming Class"
    
    # First signup
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    
    # Second signup should fail
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 400
    result = response.json()
    assert "Student already signed up" in result["detail"]


def test_signup_invalid_activity():
    """Test signup for non-existent activity"""
    response = client.post("/activities/NonExistent/signup?email=test@mergington.edu")
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" in result["detail"]


def test_unregister_success():
    """Test successful unregistration"""
    email = "removetest@mergington.edu"
    activity = "Gym Class"
    
    # First signup
    client.post(f"/activities/{activity}/signup?email={email}")
    
    # Initial count
    response = client.get("/activities")
    initial_count = len(response.json()[activity]["participants"])
    
    # Unregister
    response = client.delete(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    result = response.json()
    assert f"Unregistered {email} from {activity}" in result["message"]
    
    # Verify removed
    response = client.get("/activities")
    data = response.json()
    assert email not in data[activity]["participants"]
    assert len(data[activity]["participants"]) == initial_count - 1


def test_unregister_not_signed_up():
    """Test unregistering someone not signed up"""
    email = "notsignedup@mergington.edu"
    activity = "Debate Team"
    
    response = client.delete(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 400
    result = response.json()
    assert "Student not signed up" in result["detail"]


def test_unregister_invalid_activity():
    """Test unregister from non-existent activity"""
    response = client.delete("/activities/NonExistent/signup?email=test@mergington.edu")
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" in result["detail"]