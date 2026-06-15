import logging
import httpx
from typing import Optional, Dict, Any
from core.config import settings

logger = logging.getLogger(__name__)


class GPSService:
    def __init__(self):
        self.google_maps_key = settings.GOOGLE_MAPS_API_KEY

    async def get_route_distance(self, origin: str, destination: str) -> Optional[Dict[str, Any]]:
        """Get route distance and duration.
        FREE: Uses OpenStreetMap's Nominatim + OSRM (no API key needed!)
        Falls back to Google Maps if configured."""
        # Try OSRM first (completely free, no API key)
        try:
            origin_encoded = origin.replace(" ", "%20")
            dest_encoded = destination.replace(" ", "%20")
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    f"https://router.project-osrm.org/route/v1/driving/"
                    f"{origin_encoded},{dest_encoded}?overview=false"
                )
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("code") == "Ok" and data["routes"]:
                        route = data["routes"][0]
                        return {
                            "distance_km": round(route["distance"] / 1000, 2),
                            "duration_hours": round(route["duration"] / 3600, 2),
                            "duration_text": f"{int(route['duration'] // 3600)}h {int((route['duration'] % 3600) // 60)}m",
                            "distance_text": f"{round(route['distance'] / 1000, 1)} km",
                            "source": "osrm",
                        }
        except Exception as e:
            logger.warning(f"OSRM routing failed (fallback): {e}")

        # Fallback to Google Maps if configured
        if self.google_maps_key:
            try:
                async with httpx.AsyncClient(timeout=10) as client:
                    resp = await client.get(
                        "https://maps.googleapis.com/maps/api/distancematrix/json",
                        params={"origins": origin, "destinations": destination, "key": self.google_maps_key},
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        if data.get("status") == "OK":
                            element = data["rows"][0]["elements"][0]
                            return {
                                "distance_km": element["distance"]["value"] / 1000,
                                "duration_hours": element["duration"]["value"] / 3600,
                                "duration_text": element["duration"]["text"],
                                "distance_text": element["distance"]["text"],
                                "source": "google",
                            }
            except Exception as e:
                logger.warning(f"Google Maps failed: {e}")

        # Ultimate fallback: estimate
        logger.info(f"[GPS MOCK] Estimating route: {origin} -> {destination}")
        return {
            "distance_km": 150.0,
            "duration_hours": 2.5,
            "duration_text": "2h 30m",
            "distance_text": "150 km",
            "source": "estimated",
        }

    async def get_route_polyline(self, origin: str, destination: str) -> Optional[str]:
        """Get route polyline for map display. FREE via OSRM."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    f"https://router.project-osrm.org/route/v1/driving/"
                    f"{origin},{destination}?geometries=geojson"
                )
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("code") == "Ok" and data["routes"]:
                        import json
                        return json.dumps(data["routes"][0]["geometry"])
        except Exception as e:
            logger.warning(f"OSRM polyline failed: {e}")
        return None

    async def geocode(self, query: str) -> Optional[Dict[str, float]]:
        """Geocode an address to lat/lng. FREE via Nominatim."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    "https://nominatim.openstreetmap.org/search",
                    params={"q": query, "format": "json", "limit": 1},
                    headers={"User-Agent": settings.OSM_USER_AGENT},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    if data:
                        return {"lat": float(data[0]["lat"]), "lng": float(data[0]["lon"])}
        except Exception as e:
            logger.warning(f"Geocoding failed: {e}")
        return None


gps_service = GPSService()
