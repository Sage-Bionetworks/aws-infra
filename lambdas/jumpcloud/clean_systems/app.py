# Inactive systems on jumpcloud can clutter up the jumpcloud UI which
# makes it difficult to use.  This lambda script is used to clean up
# Jumpcloud systems that have either been removed or stopped.
from __future__ import print_function
import json
import logging
import os
import jcapiv1
from jcapiv1.rest import ApiException

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):

    logger.debug("Received event: " + json.dumps(event, sort_keys=True))

    # These should be passed in via Lambda Environment Variables
    try:
        JC_SERVICE_API_KEY = os.environ['JC_SERVICE_API_KEY']
    except (KeyError, ValueError, Exception) as e:
        logger.error(e.response['Error']['Message'])

    # Configure API key authorization: x-api-key
    configuration = jcapiv1.Configuration()
    configuration.api_key['x-api-key'] = JC_SERVICE_API_KEY
    # Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
    # configuration.api_key_prefix['x-api-key'] = 'Bearer'

    # create an instance of the API class
    api_instance = jcapiv1.SystemsApi(jcapiv1.ApiClient(configuration))
    content_type = 'application/json'  # str |  (default to application/json)
    accept = 'application/json'  # str |  (default to application/json)
    fields = 'id active last_contact'  # str | Use a space seperated string of field parameters to include the data in the response. If omitted, the default list of fields will be returned.  (optional) (default to )
    limit = 100  # int | The number of records to return at once. Limited to 100. (optional) (default to 10)
    x_org_id = ''  # str |  (optional) (default to )
    search = 'search_example'  # str | A nested object containing a string `searchTerm` and a list of `fields` to search on. (optional)
    skip = 0  # int | The offset into the records to return. (optional) (default to 0)
    sort = ''  # str | Use space separated sort parameters to sort the collection. Default sort is ascending. Prefix with `-` to sort descending.  (optional) (default to )
    filter = 'filter_example'  # str | A filter to apply to the query. (optional)

    try:
        api_response = api_instance.systems_list(content_type, accept, fields=fields, limit=limit, skip=skip, sort=sort)
        systems = api_response.results
        # remove inactive systems from jumpcloud
        for system in systems:
            if (not system.active):
                del_response = api_instance.systems_delete(system.id, content_type, accept)
                logging.info("Removed Jumpcloud System: %s" % del_response.id)

    except ApiException as e:
        print("Exception when calling SystemsApi: %s\n" % e)


if __name__ == "__main__":
    lambda_handler("event","context")
