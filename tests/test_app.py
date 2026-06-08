import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
initial_activities = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def restore_activities():
    yield
    activities.clear()
    activities.update(copy.deepcopy(initial_activities))


def test_root_redirects_to_static_index():
    # Arrange
    url = "/"

    # Act
    response = client.get(url, allow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_list():
    # Arrange
    url = "/activities"

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == 200
    assert response.json() == initial_activities


def test_signup_for_activity_adds_participant():
    # Arrange
    email = "newstudent@mergington.edu"
    activity_name = quote("Programming Class", safe="")
    url = f"/activities/{activity_name}/signup"

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Programming Class"}
    assert email in activities["Programming Class"]["participants"]


def test_signup_for_missing_activity_returns_404():
    # Arrange
    url = "/activities/Nonexistent%20Club/signup"
    email = "student@mergington.edu"

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
