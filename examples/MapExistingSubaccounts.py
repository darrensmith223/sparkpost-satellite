"""
Map a set of existing subaccounts to a satellite account and creates the webhook to relay event data for each
subaccount to the satellite account.
"""
import sparkpostsatellite
import os

# Initialize Variables
subaccount_name = "Webhook From Python"
central_api_key = os.environ.get("CENTRAL_API_KEY")
satellite_api_key = os.environ.get("SATELLITE_API_KEY")
map_file_path = "/examples/subaccounts-example-csv.csv"

# Map existing subaccounts to a satellite account
sparkpostsatellite.map_existing_mailstreams(central_api_key, satellite_api_key, map_file_path)
