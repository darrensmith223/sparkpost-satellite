import json
import boto3
import botocore
import os
import urllib3
import gzip
from urllib.parse import urlparse, urljoin


def lambda_handler(event, context):
    headers = event.get('headers')
    cfg = getConfig(headers)
    batch_id = headers.get('x-messagesystems-batch-id')
    body = event.get('body')

    # store file in S3
    s3_client = boto3.client('s3')
    store_batch(s3_client, body, batch_id)
    process_batch(json.loads(body), batch_id, cfg)

    return {
        'statusCode': 200,
        'body': 'Done'
    }


def store_batch(s3_client, body, batch_id):
    bucket_name = 'cst-darren'
    path = 'Satellite Account/' + str(batch_id)
    try:
        try:
            _ = s3_client.get_object(Bucket=bucket_name, Key=path)
            return

        except botocore.exceptions.ClientError as err:
            e = err.response['Error']['Code']
            if e in ['NoSuchKey', 'AccessDenied']:
                # Forward path. Object does not exist already, so try to create it
                s3_client.put_object(Body=body, Bucket=bucket_name, Key=path)
            else:
                print(err)

    except Exception as err:
        print(err)
        return


# Process a batch of events coming from SparkPost
def process_batch(body, batch_id, cfg):
    active_event_types = ['track_event', 'message_event', 'gen_event', 'unsubscribe_event']
    ignored_event_types = ['relay_event', 'ab_test_event', 'ingest_event']

    batch = IngestBatch()
    for i in body:
        event = i.get('msys')
        # search for which key is present in this event. Some we want, some ignored.
        found = False
        for t in active_event_types:
            if t in event:
                found = True
                batch.append(t, event.get(t))
                break
        for t in ignored_event_types:
            if t in event:
                found = True
                print('Ignored:', t)
                break
        if not found:
            print('unknown event type', i)
            break
    batch.send_to_ingest(cfg)


spc_to_ingest_type_mapping = {
    'injection': 'reception',
    'delivery': 'delivery',  # same
    'initial_open': 'initial_open',  # same
    'open': 'open',  # same
    'click': 'click',  # same
    'amp_initial_open': 'amp_initial_open',  # same
    'amp_open': 'amp_open',  # same
    'amp_click': 'amp_click',  # same
    'sms_status': 'sms_status',  # same
    'bounce': 'inband',
    'out_of_band': 'outofband',
    'spam_complaint': 'feedback',
    'delay': 'tempfail',
    'policy_rejection': 'rejection',
    'generation_rejection': 'gen_rejection',
    'generation_failure': 'gen_fail',
    'link_unsubscribe': 'link',
    'list_unsubscribe': 'list',
}


class IngestBatch:
    def __init__(self):
        self.batch = []

    # Build an Ingest API compatible event batch - mapping the inner event name from SparkPost to Momentum names
    def append(self, t, event):
        # Map and anonymize as required
        event['type'] = spc_to_ingest_type_mapping[event.get('type')]
        # event['rcpt_to'] = event.get('rcpt_to')
        # event['raw_rcpt_to'] = event.get('raw_rcpt_to')
        event['subaccount_id'] = 0  # Placeholder for mapping at ingest time

        self.batch.append((t, event))

    # Send the collected events to each ingest account / subaccount pair in turn
    def send_to_ingest(self, cfg):
        http = urllib3.PoolManager()
        api_key = cfg.get('ingest').get('api_key')
        mapped_subaccount_id = cfg.get('ingest').get('subaccount_id')

        headers = {
            'Content-Type': 'application/x-ndjson',
            'Content-Encoding': 'gzip',
            'Authorization': api_key,
        }

        # Compose and append each event into NDJSON string format
        batch_str = ''
        for t, event in self.batch:
            event['subaccount_id'] = mapped_subaccount_id
            e = {
                'msys': {
                    t: event,
                }
            }
            batch_str += json.dumps(e, indent=None, separators=None) + '\n'

        compressed_events = gzip.compress(batch_str.encode('utf-8'))

        res = http.request(method='POST', url=cfg.get('ingest').get('url'), body=compressed_events, headers=headers)
        print('Ingest upload results:', res.status, res.data.decode('utf-8'))


def getApiKey():
    api_key = os.getenv('SPARKPOST_API_KEY_304459')
    return api_key


def get_mapped_subaccount_id():
    subaccount_id = 0
    return subaccount_id


def host_cleanup(host):
    if host == None:
        return None
    u = urlparse(host, scheme='https', allow_fragments=True)  # prepend the scheme if not already in the host string
    return u.geturl()


def getConfig(headers):
    host = host_cleanup(os.getenv('SPARKPOST_HOST', default='https://api.sparkpost.com'))
    url = urljoin(host, '/api/v1/ingest/events')
    customer_id = headers.get('x-customer-id')
    subaccount_id = headers.get('x-subaccount-id')
    api_key = os.getenv('SPARKPOST_API_KEY_' + str(customer_id))

    cfg = {
        'ingest': {
            'url': url,
            'api_key': api_key,
            'subaccount_id': str(subaccount_id)
        }
    }
    return cfg