"""
Real-time Weather Tool for NPCL Voice Assistant (RealTimeOpenAI-Basic)
Provides actual weather information using OpenWeatherMap API with OpenAI function calling.
"""

import asyncio
import aiohttp
import time
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class WeatherTool:
    """Real-time weather information tool using OpenWeatherMap API"""
    
    def __init__(self):
        self.api_key = os.getenv('WEATHER_API_KEY')
        self.base_url = os.getenv('WEATHER_API_BASE_URL', 'https://api.openweathermap.org/data/2.5')
        self.cache = {}  # Simple cache to avoid rate limits
        self.cache_duration = 600  # 10 minutes cache
        
        # City name mappings for better API results
        self.city_mappings = {
            "New Delhi": "Delhi,IN",
            "Bombay": "Mumbai,IN", 
            "Calcutta": "Kolkata,IN",
            "Bengaluru": "Bangalore,IN",
            "Madras": "Chennai,IN",
            "Gurgaon": "Gurugram,IN",
            "Trivandrum": "Thiruvananthapuram,IN",
            "Vizag": "Visakhapatnam,IN",
            
            # NPCL service areas - ensure proper state/country codes
            "Noida": "Noida,UP,IN",
            "Greater Noida": "Greater Noida,UP,IN", 
            "Ghaziabad": "Ghaziabad,UP,IN",
            "Faridabad": "Faridabad,HR,IN",
            "Gurugram": "Gurugram,HR,IN"
        }
    
    def get_function_definition(self) -> Dict[str, Any]:
        """Get OpenAI function definition for weather lookup"""
        return {
            "name": "get_weather",
            "description": "Get real-time weather information for cities in India, especially NCR region served by NPCL. Provides current temperature, conditions, humidity, and wind information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name in India (Delhi, Mumbai, Bangalore, Chennai, Kolkata, Noida, Greater Noida, Ghaziabad, Faridabad, Gurugram, etc.)"
                    }
                },
                "required": ["location"]
            }
        }
    
    async def execute(self, location: str) -> str:
        """
        Execute real-time weather lookup for the specified location.
        
        Args:
            location: City name to get weather for
            
        Returns:
            Weather information as formatted string
        """
        try:
            # Check if API key is available
            if not self.api_key:
                return "Weather service is currently unavailable. Please contact support for weather information."
            
            # Normalize location name
            location_normalized = self._normalize_location(location)
            
            # Check cache first
            cached_data = self._get_cached_weather(location_normalized)
            if cached_data:
                return cached_data
            
            # Fetch real-time weather data
            weather_data = await self._fetch_weather_data(location_normalized)
            
            if weather_data:
                # Format response
                result = self._format_weather_response(location, weather_data)
                
                # Cache the result
                self._cache_weather(location_normalized, result)
                
                return result
            else:
                # Fallback response
                return f"Sorry, I couldn't get current weather information for {location}. Please try with a major Indian city name like Delhi, Mumbai, or Bangalore."
                
        except Exception as e:
            return f"Weather service is temporarily unavailable for {location}. Please try again later or contact support for assistance."
    
    def _normalize_location(self, location: str) -> str:
        """Normalize location name for API lookup"""
        location = location.strip().title()
        
        # Use mapping if available, otherwise add country code
        if location in self.city_mappings:
            return self.city_mappings[location]
        else:
            # Add India country code for better API results
            return f"{location},IN"
    
    async def _fetch_weather_data(self, location: str) -> Optional[Dict[str, Any]]:
        """Fetch real-time weather data from OpenWeatherMap API"""
        try:
            url = f"{self.base_url}/weather"
            params = {
                "q": location,
                "appid": self.api_key,
                "units": "metric",  # Celsius
                "lang": "en"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    elif response.status == 404:
                        return None
                    elif response.status == 401:
                        return None
                    else:
                        return None
                        
        except asyncio.TimeoutError:
            return None
        except Exception:
            return None
    
    def _format_weather_response(self, original_location: str, weather_data: Dict[str, Any]) -> str:
        """Format weather response for voice assistant"""
        try:
            # Extract data from API response
            city_name = weather_data["name"]
            country = weather_data["sys"]["country"]
            temp = round(weather_data["main"]["temp"])
            feels_like = round(weather_data["main"]["feels_like"])
            humidity = weather_data["main"]["humidity"]
            description = weather_data["weather"][0]["description"].title()
            wind_speed = weather_data["wind"]["speed"]
            wind_direction = self._get_wind_direction(weather_data["wind"].get("deg", 0))
            
            # Check if it's an NPCL service area
            npcl_areas = ["Noida", "Greater Noida", "Ghaziabad", "Faridabad", "Gurugram"]
            is_npcl_area = any(area.lower() in city_name.lower() for area in npcl_areas)
            
            # Create natural language response
            if is_npcl_area:
                response = (
                    f"Current weather in {city_name}: {temp}°C with {description.lower()}. "
                    f"It feels like {feels_like}°C. Humidity is {humidity}%. "
                    f"Wind is {wind_speed} m/s from the {wind_direction}. "
                    f"This is in the NPCL service area - power supply should remain stable in these weather conditions."
                )
            else:
                response = (
                    f"Current weather in {city_name}: {temp}°C with {description.lower()}. "
                    f"It feels like {feels_like}°C. Humidity is {humidity}%. "
                    f"Wind is {wind_speed} m/s from the {wind_direction}."
                )
            
            return response
            
        except KeyError:
            return f"Weather data received for {original_location}, but some information is incomplete."
    
    def _get_wind_direction(self, degrees: float) -> str:
        """Convert wind degrees to direction"""
        directions = [
            "north", "north-northeast", "northeast", "east-northeast",
            "east", "east-southeast", "southeast", "south-southeast", 
            "south", "south-southwest", "southwest", "west-southwest",
            "west", "west-northwest", "northwest", "north-northwest"
        ]
        
        index = round(degrees / 22.5) % 16
        return directions[index]
    
    def _get_cached_weather(self, location: str) -> Optional[str]:
        """Get cached weather data if still valid"""
        if location in self.cache:
            cached_time, cached_result = self.cache[location]
            if time.time() - cached_time < self.cache_duration:
                return cached_result
        return None
    
    def _cache_weather(self, location: str, result: str):
        """Cache weather result"""
        self.cache[location] = (time.time(), result)
        
        # Clean old cache entries (keep only last 50)
        if len(self.cache) > 50:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][0])
            del self.cache[oldest_key]

# Create weather tool instance
weather_tool = WeatherTool()