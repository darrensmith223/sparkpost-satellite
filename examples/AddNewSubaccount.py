"""
Add a new subaccount to a central account and map to a satellite account.  Also creates the webhook to relay event data
to the satellite account.
"""
import sparkpostsatellite
import os


subaccount_name = "Webhook From Python"
central_api_key = os.environ.get("CENTRAL_API_KEY")
satellite_api_key = os.environ.get("SATELLITE_API_KEY")

# Add New Mail Stream
sparkpostsatellite.add_new_mailstream(subaccount_name, central_api_key, satellite_api_key)
