"""
Collects addresses from the intarwebs
"""

import sys
import json
import urllib
import urllib2


SEARCH_URL = 'https://maps.googleapis.com/maps/api/place/textsearch/json?{}'
DETAILS_URL = 'https://maps.googleapis.com/maps/api/place/details/json?{}'


class APICommunicationError(Exception):
    pass


def check_return(result, default_error=None):
    """
    Verifies that the result from google is not an error
    """
    error_message = None

    if not result.get('status') == 'OK':
        if 'error_message' in result:
            error_message = result['error_message']
        else:
            if not default_error:
                error_message = 'Invalid data returned from Google due to ' \
                                'an unknown problem.'
            else:
                error_message = default_error

    return error_message


def collect(query, api_key):
    search_params = urllib.urlencode({
        'query': query,
        'key': api_key
    })

    search = SEARCH_URL.format(search_params)
    query_result = json.load(urllib2.urlopen(search))

    if check_return(query_result):
        raise APICommunicationError(check_return(query_result))

    details_params = urllib.urlencode({
        'placeid': query_result['results'][0]['place_id'],
        'key': api_key
    })

    details = DETAILS_URL.format(details_params)
    detail_results = json.load(urllib2.urlopen(details))

    if check_return(detail_results):
        raise APICommunicationError(check_return(detail_results))

    return detail_results['result']['formatted_address']


if __name__ == '__main__':
    if not len(sys.argv) == 3:
        print 'USAGE: {} INPUT_FILE API_KEY'.format(sys.argv[0])
        sys.exit(1)

    with open(sys.argv[1]) as fp:
        for place in fp.read().split('\n'):
            if place.strip():
                try:
                    address = collect(place.strip(), sys.argv[2])
                    print '{}:: {}'.format(place.strip(), address)
                except APICommunicationError as e:
                    error = 'Error communicating with the server: {}'.format(
                        e.message
                    )

                    sys.stderr.write(error + '\n')
                    sys.exit(1)
