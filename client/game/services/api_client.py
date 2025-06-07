"""
API client for communicating with the FixieDashBrooklyn backend server.
"""

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional


class APIClient:
    """Client for communicating with the backend API."""

    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url.rstrip("/")
        self.session_id: Optional[str] = None
        self.user_id: Optional[str] = None

    def _make_request(
        self, method: str, endpoint: str, data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to the backend."""
        url = f"{self.base_url}{endpoint}"

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "FixieDashBrooklyn-Client/1.0",
        }

        request_data = None
        if data:
            request_data = json.dumps(data).encode("utf-8")

        try:
            if method.upper() == "GET":
                req = urllib.request.Request(url, headers=headers)
            else:
                req = urllib.request.Request(url, data=request_data, headers=headers)
                req.get_method = lambda: method.upper()

            with urllib.request.urlopen(req, timeout=10) as response:
                response_data = response.read().decode("utf-8")
                return json.loads(response_data)

        except urllib.error.HTTPError as e:
            error_data = e.read().decode("utf-8")
            try:
                error_json = json.loads(error_data)
                return {"success": False, "error": error_json.get("error", str(e))}
            except json.JSONDecodeError:
                return {"success": False, "error": f"HTTP {e.code}: {e.reason}"}
        except Exception as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}

    def register_user(
        self, username: str, email: Optional[str] = None
    ) -> Dict[str, Any]:
        """Register a new user."""
        data = {"username": username}
        if email:
            data["email"] = email

        response = self._make_request("POST", "/api/users/register", data)
        if response.get("success") and "user" in response:
            self.user_id = response["user"]["id"]
        return response

    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile information."""
        return self._make_request("GET", f"/api/users/{user_id}")

    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user statistics."""
        return self._make_request("GET", f"/api/users/{user_id}/stats")

    def start_game_session(self, user_id: str) -> Dict[str, Any]:
        """Start a new game session."""
        data = {"playerId": user_id}
        response = self._make_request("POST", "/api/game/start", data)
        if response.get("success") and "sessionId" in response:
            self.session_id = response["sessionId"]
        return response

    def end_game_session(
        self,
        session_id: str,
        max_speed: float,
        total_distance: float,
        completion_time: float,
    ) -> Dict[str, Any]:
        """End game session and submit score."""
        data = {
            "sessionId": session_id,
            "maxSpeed": max_speed,
            "totalDistance": total_distance,
            "completionTime": completion_time,
        }
        response = self._make_request("POST", "/api/game/end", data)
        self.session_id = None
        return response

    def get_leaderboard(self, limit: int = 10) -> Dict[str, Any]:
        """Get top scores from leaderboard."""
        return self._make_request("GET", f"/api/leaderboard/top/{limit}")

    def health_check(self) -> Dict[str, Any]:
        """Check if the backend server is healthy."""
        return self._make_request("GET", "/health")

    def is_server_available(self) -> bool:
        """Check if the server is available."""
        response = self.health_check()
        return response.get("success", False) or "status" in response
