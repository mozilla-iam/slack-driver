#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# Copyright (c) 2018 Mozilla Corporation
# Contributors: Guillaume Destuynder <kang@mozilla.com>

# This file exists because: https://github.com/slackapi/python-slackclient/issues/292
# At this time there is no SCIM API library
# See also https://api.slack.com/scim#access

import http.client
import json
import time

class SlackAPI(object):
    def __init__(self, token, uri="api.slack.com"):
        self.headers = {
                'content-type': "application/json",
                'Authorization': "Bearer {}".format(token)
        }
        self.conn = http.client.HTTPSConnection(uri)

    def __del__(self):
        self.headers = None

    def _request(self, rtype, rpath, payload_json={}):
        """
        Wraps all API requests
        """
        self.conn.request(rtype, rpath, payload_json, self.headers)
        response = self.conn.getresponse()

        if (response.status >= 300) or (response.status < 200):
            raise Exception('HTTPCommunicationFailed', (response.status, response.reason, rpath, payload_json))

        ret = json.loads(response.read().decode('utf-8'))
        return ret

    def _depaginated_request(self, rtype, rpath, payload_json={}):
        """
        Returns all results from a paginated request
        """
        count = 0
        results = []

        res = self._depaginate(self._request(rtype, rpath, payload_json))
        results += res.get('results')
        while (not res.get('done')):
            res = self._depaginate(self._request(rtype, rpath, payload_json))
            results += res.get('results')
        return results

    def _depaginate(self, response):
        """
        Checks if we need to depaginate the request result, and return that fact in addition to the actual results of
        the request
        """
        # note that slack index starts at 1 instead of 0, so we fix that
        index = response.get('startIndex')-1
        totals = response.get('totalResults')
        per_page = response.get('itemsPerPage')
        results = response.get('Resources')
        ret = {'done': False, 'results': results}

        # is there more pages left than total pages?
        # otherwise we're done
        if index+per_page >= totals:
            ret['done'] = True

        return ret

    def get_users(self, scim_filter=''):
        """
        Ex scim_filter: userName%20Eq%20kang_slack
        See also https://api.slack.com/scim#users
        and https://api.slack.com/scim#filter for the scim_filter syntax

        Returns list, similar to:
        [{'schemas': ['urn:scim:schemas:core:1.0'], 'id': 'UB0GWPDCM', 'externalId': '', 'meta': {'created': '2018-06-01T16:10:18-07:00', 'location': 'https://api.slack.com/scim/v1/Users/UB0GWPDCM'}, 'userName': 'kang_slack', 'nickName': 'kang_slack', 'name': {'givenName': '', 'familyName': ''}, 'displayName': '', 'profileUrl': 'https://mozilla-sandbox-scim.slack.com/team/kang_slack', 'title': '', 'timezone': 'America/Los_Angeles', 'active': False, 'emails': [{'value': 'kang+slack@mozilla.com', 'primary': True}], 'photos': [{'value': 'https://secure.gravatar.com/avatar/8363a16c1147ee60fff6be4c8b30aaa1.jpg?s=192&d=https%3A%2F%2Fcfr.slack-edge.com%2F7fa9%2Fimg%2Favatars%2Fava_0009-192.png', 'type': 'photo'}], 'groups': []}]

        """
        return self._depaginated_request("GET", "/scim/v1/Users?filter={}".format(scim_filter))

    def deactivate_user(self, slack_user_id):
        """
        See also https://api.slack.com/scim#users
        """
        payload = {'active': False}
        payload_json = json.dumps(payload)
        return self._request("PATCH", "/scim/v1/Users/{}".format(slack_user_id), payload_json)
