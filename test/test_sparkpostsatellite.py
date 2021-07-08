import sparkpostsatellite
import responses


@responses.activate
def test_get_customer_id():
    api_url = "https://api.sparkpost.com/api/v1/account"
    responses.add(
        responses.GET,
        api_url,
        status=200,
        content_type='application/json',
        body='{"results": {"customer_id": 102938}}'
    )

    # get customer_id
    api_key = "fake-key"
    response = sparkpostsatellite.get_customer_id(api_key)
