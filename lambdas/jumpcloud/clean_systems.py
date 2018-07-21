# This script is used to periodically clean up Jumpcloud "systems" that have been removed from AWS
from __future__ import print_function
import logging
import jcapiv1
import os
from jcapiv1.rest import ApiException
from datetime import datetime, timedelta

def lambda_handler(event, context):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    jcapiv1.configuration.api_key['x-api-key'] = os.environ['JC_SERVICE_API_KEY']
    # Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
    # jcapiv1.configuration.api_key_prefix['x-api-key'] = 'Bearer'

    # create an instance of the API class
    api_instance = jcapiv1.SystemsApi()
    content_type = 'application/json' # str |  (default to application/json)
    accept = 'application/json' # str |  (default to application/json)
    fields = 'id,active' # str | The comma separated fields included in the returned records. If omitted the default list of fields will be returned.  (optional) (default to )
    limit = 500 # int | The number of records to return at once. (optional) (default to 10)
    skip = 0 # int | The offset into the records to return. (optional) (default to 0)
    sort = '' # str | The comma separated fields used to sort the collection. Default sort is ascending, prefix with `-` to sort descending.  (optional) (default to )

    last_hour_date_time = datetime.utcnow() - timedelta(hours = 1)
    logging.info("Last hour time: %s" % last_hour_date_time.strftime("%Y-%m-%d %H:%M:%S"))
    try:
        api_response = api_instance.systems_list(content_type, accept, limit=limit)
        systems = api_response.results
        # delete inactive systems that have not synced in the past hour
        for system in systems:
            last_contact_date_time = datetime.strptime(system.last_contact[:19], '%Y-%m-%dT%H:%M:%S')
            if (not system.active and last_contact_date_time < last_hour_date_time):
                del_response = api_instance.systems_delete(system.id, content_type, accept)
                logging.info("Removed Jumpcloud System: %s" % del_response.id)

    except ApiException as e:
        print("Exception when calling SystemsApi: %s\n" % e)


if __name__ == "__main__":
    lambda_handler("event","context")
