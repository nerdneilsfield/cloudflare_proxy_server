#!/bin/env python

import requests as rq
import json


class DDNS_updater(object):
    def __init__(self, email : str, api_key: str):
        self.email = email
        self.api_key = api_key
        self.EXTERNAL_IP_QUERY_API = 'https://api.ipify.org/?format=json'
        self.CLOUDFLARE_ZONE_QUERY_API = 'https://api.cloudflare.com/client/v4/zones?per_page=50'  # GET
        self.CLOUDFLARE_ZONE_DNS_RECORDS_QUERY_API = 'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records'  # GET
        self.CLOUDFLARE_ZONE_DNS_RECORDS_UPDATE_API = 'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{dns_record_id}'  # PUT
        self.auth = {'X-Auth-Email': self.email, 'X-Auth-Key': self.api_key}
        self.zones = {}
        self.records = {}

    def update_zones(self):
        res = rq.get(
            self.CLOUDFLARE_ZONE_QUERY_API,
            headers=self.auth,
            timeout=15
        ).json()['result']

        for result in res:
            self.zones[result["name"]] = result["id"]

            records_res = rq.get(
                self.CLOUDFLARE_ZONE_DNS_RECORDS_QUERY_API.format(zone_id=result['id']),
                headers = self.auth,
                timeout = 15,
                ).json()['result']
            for record in records_res:
                record_data = {}
                record_data['id']  = record['id']
                record_data['type'] = record['type']
                record_data['name'] = record['name']
                record_data['content'] = record['content']
                self.records[record['name']] = record_data

    def create_record(self, domain_id, record, record_type, content):
        res = rq.post(
            self.CLOUDFLARE_ZONE_DNS_RECORDS_QUERY_API.format(
                zone_id = domain_id,
            ),
            headers = self.auth,
            data = json.dumps({
                'type': record_type,
                'name': record,
                'content': content,
            })
        )

        if res.json()['success']:
            return {
                "success": True
            }
        else:
            return {
                'success': False,
                'message': "error create {domain}".format(domain=record) + '\n'.join(res.json()['messages'])
            }

    def update_exist_record(self, domain_id, record_id, record, record_type, content):

        res = rq.put(
            self.CLOUDFLARE_ZONE_DNS_RECORDS_UPDATE_API.format(
                zone_id = domain_id,
                dns_record_id = record_id
            ),
            headers = self.auth,
            data = json.dumps({
                'type': record_type,
                'name': record,
                'content': content,
            })
        )

        if res.json()['success']:
            return {
                "success": True
            }
        else:
            return {
                'success': False,
                'message': '\n'.join(res.json()['messages'])
            }

    def update_record(self, record, record_type, content):
        record_type = record_type.upper()
        if record_type not in ['A', 'AAA', 'TXT', 'CNAME']:
            return {
                'success': False,
                'message': "Not support such type : {type}".format(type=record_type),
            }
        domain = '.'.join(record.split('.')[-2:])
        refresh = False
        if domain not in self.zones.keys():
            self.update_zones()
            self.refresh = True
            if domain not in self.zones.keys():
                return {
                    "success": False,
                    "message": "No such domain {domain}".format(domain=domain),
                }
        domain_id = self.zones[domain]
        if record not in self.records.keys():
            if not refresh:
                self.update_zones()
            if record not in self.records.keys():
                return self.create_record(domain_id, record, record_type, content)
        if self.records[record]['type'] != record_type:
            return self.create_record(domain_id, record, record_type, content)
        record_id = self.records[record]['id']
        if content == self.records[record]['content']:
            return {
                'success': False,
                'message':"No need for update record!"
            }
        self.update_exist_record(domain_id, record, record_id, record_type, content)
