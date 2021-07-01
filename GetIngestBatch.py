import os
import requests
import gzip

ingest_id = "PASTE_ID_HERE"
api_key = os.environ.get("SATELLITE_API_KEY")
api_url = "https://api.sparkpost.com/api/v1/ingest/events/" + str(ingest_id)
apiHeaders = {
    "Authorization": api_key
}
response = requests.get(api_url, headers=apiHeaders)
package_data = response.content
uncompressed_events = gzip.decompress(package_data)
print(uncompressed_events)
