"""
Manage mailstreams between central and satellite accounts.
"""
import requests
import json
import csv


def add_subaccount(api_key, subaccount_name):
    api_url = "https://api.sparkpost.com/api/v1/subaccounts"
    api_data = {
        "name": subaccount_name,
        "setup_api_key": False
    }

    response = make_api_call("POST", api_key, api_url, api_data=api_data)
    subaccount_id = response.json()['results']["subaccount_id"]
    return subaccount_id


def add_webhook(api_key, subaccount_name, central_subaccount_id, satellite_customer_id, satellite_subaccount_id):
    if len(subaccount_name) >= 24:
        subaccount_name = subaccount_name[:23]

    # get all current event types
    events_list = get_all_event_types(api_key)

    # create webhook
    api_url = "https://api.sparkpost.com/api/v1/webhooks"
    api_data = {
        "name": subaccount_name,
        "target": "https://satellite.trymsys.net",
        "custom_headers": {
            "x-customer-id": str(satellite_customer_id),
            "x-subaccount-id": str(satellite_subaccount_id)
        },
        "events": events_list
    }
    response = make_api_call("POST", api_key, api_url, api_data=api_data, subaccount_id=central_subaccount_id)
    return response


def get_all_event_types(api_key):
    # get all event types
    api_url = "https://api.sparkpost.com/api/v1/webhooks/events/documentation"
    response = make_api_call("GET", api_key, api_url)
    active_event_types = ['track_event', 'message_event', 'gen_event', 'unsubscribe_event']
    events_list = []
    events_obj = response.json()["results"]
    for event_type in active_event_types:
        if event_type in events_obj:
            for event in response.json()["results"][event_type]["events"]:
                events_list.append(event)

    return events_list


def get_customer_id(api_key):
    # get customer_id
    api_url = "https://api.sparkpost.com/api/v1/account"
    response = make_api_call("GET", api_key, api_url)
    customer_id = response.json()["results"]["customer_id"]
    return customer_id


def make_api_call(api_type, api_key, api_url, api_data=None, subaccount_id=None):
    # Construct API Call
    apiHeaders = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }

    if subaccount_id is not None:
        apiHeaders["X-MSYS-SUBACCOUNT"] = str(subaccount_id)

    # Make API Call
    if api_type == "POST":
        apiDataJson = json.dumps(api_data)
        response = requests.post(api_url, data=apiDataJson, headers=apiHeaders)
        return response
    elif api_type == "GET":
        response = requests.get(api_url, headers=apiHeaders)
        return response


def add_new_mailstream(subaccount_name, central_api_key, satellite_api_key):
    """
    Add a new subaccount to a central account and mirror the subaccount in a satellite account.  Also creates the
    webhook in the central account to relay events to the satellite account.

    :param str subaccount_name:  Name assigned to the new subaccounts
    :param str central_api_key:  API key used to authenticate the central account
    :param satellite_api_key:  API key used to authenticate the satellite account
    :return: None
    """
    # Add new subaccount to central sending account
    central_subaccount_id = add_subaccount(central_api_key, subaccount_name)

    # Add new subaccount to satellite account
    satellite_subaccount_id = add_subaccount(satellite_api_key, subaccount_name)

    # Add new webhook to central account
    satellite_customer_id = get_customer_id(satellite_api_key)
    response = add_webhook(central_api_key, subaccount_name, central_subaccount_id, satellite_customer_id,
                           satellite_subaccount_id)


def map_existing_mailstreams(central_api_key, satellite_api_key, map_file_path):
    """
    Map the existing subaccounts from the central account to a new satellite account.  Also creates the
    webhook in the central account to relay events to the satellite account for each subaccount.

    :param str central_api_key:  API key used to authenticate the central account
    :param satellite_api_key:  API key used to authenticate the satellite account
    :param map_file_path:  Full path to the csv file containing the subaccount ID and name of all existing subaccounts
        that need to be mapped into a satellite account.
    :return: None
    """
    # Read subaccount entries from CSV
    subaccount_list = []
    with open(map_file_path) as df:
        reader = csv.DictReader(df, delimiter=',')
        for row in reader:
            subaccount_list.append(row)

    # Create subaccount and webhook mapping for each existing subaccount
    for subaccount in subaccount_list:
        central_subaccount_id = subaccount["subaccount_id"]
        subaccount_name = subaccount["subaccount_name"]

        satellite_subaccount_id = add_subaccount(satellite_api_key, subaccount_name)
        satellite_customer_id = get_customer_id(satellite_api_key)
        response = add_webhook(central_api_key, subaccount_name, central_subaccount_id, satellite_customer_id,
                               satellite_subaccount_id)
