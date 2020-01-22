import json
import logging
import math
import os
import sys
from datetime import datetime, timedelta
from time import sleep
from urllib2 import urlparse
from urllib import  urlencode

import facebook
from pyramid.paster import (get_appsettings, setup_logging, )
from pyramid.scripts.common import parse_vars
from requests.exceptions import ConnectionError
from social_insights.models import Interactions, SmAccounts

from ..utils import configure_db_session
import transaction

logger = logging.getLogger(__name__)


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def collect_fb_posts(sm_account_id, access_token, session, since=None, until=None, days=7, limit=100, cutoff=None):
    """
    Collect the facebook posts for a given facebook page
    :param sm_account_id:
    :param access_token:
    :param session:
    :param since:
    :param until:
    :param days:
    :param limit:
    :param cutoff:
    :return:
    """
    graph = facebook.GraphAPI(access_token=access_token, version='2.6')
    first_req = get_feed_request(sm_account_id, since, until, limit=limit, days=days)
    # data = pickle.load(open('sample_json.pkl', 'rb'))
    interactions = set()
    batch_requests = [first_req]
    process_batch(sm_account_id, graph, interactions, batch_requests, session, 0, cutoff)


def get_feed_request(sm_account_id, since=None, until=None, limit=100, days=7):
    """
    Get initial request using nested requests
    :param sm_account_id:
    :param since:
    :param until:
    :param limit:
    :param days: collection will be run for past n days. used only when since is not provided
    :return:
    """
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = (today - timedelta(days=days))
    if since is None:
        since = str(int(start_date.timestamp()))
    if until is None:
        until = str(int(datetime.utcnow().timestamp()))

    # TODO: raise error when since is lesser than until
    # TODO: make the comment limit as configurable
    # we  will get the post, comments up to 2 levels in a single request
    # see the section "Making Nested Requests" in the link
    # https://developers.facebook.com/docs/graph-api/using-graph-api
    path = '/v2.6/{0}/feed'.format(sm_account_id)

    fields = 'type,from,message,created_time,updated_time,\
    likes.limit(0).summary(true),comments.limit({0}){{message,from,created_time,updated_time,like_count,comment_count,\
    comments.limit({0}).since({1}).until({2}){{message,from,created_time,updated_time,like_count,comment_count,\
    comments.limit({0}).since({1}).until({2})}}}}'.format(
        limit, since, until)
    logger.debug('fields part of graph api request \n {}'.format(fields))
    first_req = {'method': 'GET', 'relative_url': path + '?' + urlencode(
        {'fields': fields, 'since': since, 'until': until, 'limit': limit})}
    return first_req


def process_batch(sm_account_id, graph, interactions, batch_requests, p_session, processed_interactions=None,
                  cutoff=None):
    """
    A function that sends batch requests to FB, collects the results and prepares the
    next set of batch requests for data corresponding to pagination.
    Call itself recursively until all posts in the given period are fetched.
    :param sm_account_id:
    :param graph:
    :param interactions:
    :param batch_requests:
    :param p_session:
    :param processed_interactions: Number of interactions already processed
    :param cutoff: stop collection if processed_interactions exceeds cutoff
    :return:
    """
    with transaction.manager:
        for interaction in interactions:
            p_session.merge(interaction)

    if len(batch_requests) == 0 or (processed_interactions and processed_interactions >= cutoff):
        return

    # process batch requests
    # Number of max items in a batch request is 50
    MAX_BATCH_SIZE = 50
    batch_requests_p = [{'method': req.get('method'), 'relative_url': req.get('relative_url')} for req in
                        batch_requests]
    batch_data = []

    interactions_new = set()
    batch_requests_new = []

    for i in range(math.ceil(len(batch_requests_p) / MAX_BATCH_SIZE)):
        # TODO handle connection error. attempt retries
        try:
            batch_req = json.dumps(batch_requests_p[i * MAX_BATCH_SIZE:(i * MAX_BATCH_SIZE) + (MAX_BATCH_SIZE - 1)],
                                   indent=1)
            batch_data += graph.request("", post_args={
                'batch': batch_req})

        except ConnectionError as e:
            logger.exception('unable to process batch request \n:{}'.format(batch_req))
    for req, batch_response in zip(batch_requests, batch_data):
        parent_id = req.get('parent_id')
        if 'body' in batch_response:
            batch_response_data = json.loads(batch_response['body'])
            if 'error' in batch_response_data and batch_response_data['error'].get('code') == 1:
                # handle request failure - 'Please reduce the amount of data you are asking for, then retry your request'
                error_url = req.get('relative_url')
                parse_result = urlparse(error_url)
                query_data = urlparse.parse_qs(parse_result.query)
                old_limit = query_data.get('limit')[0]
                sm_account_id = parse_result.path.split("/")[2]
                new_limit = int(float(old_limit) / 2)
                new_req = get_feed_request(sm_account_id, limit=new_limit)
                batch_requests_new.append(new_req)

            if 'data' in batch_response_data:
                for interaction_raw in batch_response_data['data']:
                    Interactions.get_nested_interactions(sm_account_id, interaction_raw, interactions_new,
                                                         batch_requests_new, parent_id)
            if 'paging' in batch_response_data and 'next' in batch_response_data['paging']:
                next_url = urlparse(batch_response_data['paging']['next'])
                relative_url = next_url.path + '?' + next_url.query + '&include_headers=false'
                req = {'method': 'GET', 'relative_url': relative_url, 'parent_id': parent_id}
                batch_requests_new.append(req)
        else:
            logger.info('Exception occurred while collecting posts for {} skipping this..'.format(sm_account_id))

    process_batch(sm_account_id, graph, interactions_new, batch_requests_new, p_session,
                  processed_interactions + len(interactions), cutoff)


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)
    engine, session = configure_db_session(settings)

    logger.info("Starting the facebook page posts collection")
    # process pages
    for sm_account in session.query(SmAccounts).all():
        logger.info('Processing the page: {0}'.format(sm_account.sm_domain))
        access_token = 'EAAPQpBr7UBQBAIeJbpVdpd3MPk4Q3E1as1ETNQN1zPDbZCqvUE8xgb0qATlSUU7ZCoyBZB6iyukGPjLZCG1Wo1JNcRq8B7nLYio8KEcqWosL4i2momiRywCAvrsGjLGm5KZAzd7q2ZB1qkVGKsimCBWjZBHanZASqFAZD'
        collect_fb_posts(sm_account.sm_account_id, access_token, session)
        logger.info('Completed processing the page: {0}'.format(sm_account.sm_domain))
        sleep(10)
    logger.info("Completed facebook page posts collection")
