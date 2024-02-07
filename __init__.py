"""
Open Street Routing Machine (OSRM) API
Author: Chien-Hao (Will) Huang
Version: 1.0.0

New Release on February 8, 2024:
1. Add requests timeout to avoid OSRM API having no response.
2. If there is no response from OSRM API, use the haversine distance as a substitution.
3. Users can customize their travel speeds to get different travel times if using the haversine distance.
4. If users set the `timeout` as a tiny float number (recommended <0.1),
   both the travel distance and the travel time would be calculated based on the haversine distance in many situations.

"""