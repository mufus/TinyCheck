#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import db
from app.db.models import OCTIInst
from app.definitions import definitions as defs

from sqlalchemy.sql import exists
from urllib.parse import unquote
from flask import escape
from pycti import OpenCTIApiClient, Infrastructure
import re
import time
import sys


class OCTI(object):
    def __init__(self):
        return None

    def add_instance(self, instance):
        """
            Parse and add a OpenCTI instance to the database.
            :return: status of the operation in JSON
        """

        url = instance["url"]
        name = instance["name"]
        apikey = instance["key"]
        verify = instance["ssl"]
        last_sync = int(time.time()-31536000)  # One year

        sameinstances = db.session.query(OCTIInst).filter(
            OCTIInst.url == url, OCTIInst.apikey == apikey)
        if sameinstances.count():
            return {"status": False,
                    "message": "This OpenCTI instance already exists"}
        if name:
            if self.test_instance(url, apikey, verify):
                added_on = int(time.time())
                db.session.add(OCTIInst(name, escape(
                    url), apikey, verify, added_on, last_sync))
                db.session.commit()
                return {"status": True,
                        "message": "OpenCTI instance added"}
            else:
                return {"status": False,
                        "message": "Please verify the connection to the OpenCTI instance"}
        else:
            return {"status": False,
                    "message": "Please provide a name for your instance"}

    @staticmethod
    def delete_instance(opencti_id):
        """
            Delete a OpenCTI instance by its id in the database.
            :return: status of the operation in JSON
        """
        if db.session.query(exists().where(OCTIInst.id == misp_id)).scalar():
            db.session.query(OCTIInst).filter_by(id=misp_id).delete()
            db.session.commit()
            return {"status": True,
                    "message": "OpenCTI instance deleted"}
        else:
            return {"status": False,
                    "message": "OpenCTI instance not found"}

    def get_instances(self):
        """
            Get OpenCTI instances from the database
            :return: generator of the records.
        """
        for opencti in db.session.query(OCTIInst).all():
            opencti = opencti.__dict__
            yield {"id": opencti["id"],
                   "name": opencti["name"],
                   "url": opencti["url"],
                   "apikey": opencti["apikey"],
                   "verifycert": True if opencti["verifycert"] else False,
                   "connected": self.test_instance(opencti["url"], opencti["apikey"], opencti["verifycert"]),
                   "lastsync": opencti["last_sync"]}

    @staticmethod
    def test_instance(url, apikey, verify):
        """
            Test the connection of the OpenCTI instance.
            :return: generator of the records.
        """
        try:
            OpenCTIApiClient(url, token=apikey, ssl_verify=verify)
            return True
        except:
            return False

    @staticmethod
    def update_sync(opencti_id):
        """
            Update the last synchronization date by the actual date.
            :return: bool, True if updated.
        """
        try:
            misp = OCTIInst.query.get(int(opencti_id))
            misp.last_sync = int(time.time())
            db.session.commit()
            return True
        except:
            return False

    @staticmethod
    def get_iocs(opencti_id):
        """
            Get all IOCs from specific OpenCTI instance
            :return: generator containing the IOCs.
        """
        opencti = OCTIInst.query.get(int(opencti_id))
        if opencti is not None:
            if opencti.url and opencti.apikey:
                try:
                    # Connect to OpenCTI instance and get network activity attributes.
                    i = OpenCTIApiClient(
                        opencti.url, opencti.apikey, opencti.verifycert)
                    r = Infrastructure(i).list(getAll=True)
                except:
                    print(
                        "Unable to connect to the OpenCTI instance ({}/{}).".format(opencti.url, opencti.apikey))
                    return []
                """
                for attr in r["Attribute"]:
                    if attr["type"] in ["ip-dst", "domain", "snort", "x509-fingerprint-sha1"]:

                        ioc = {"value": attr["value"],
                               "type": None,
                               "tag": "suspect",
                               "tlp": "white"}

                        # Deduce the IOC type.
                        if re.match(defs["iocs_types"][0]["regex"], attr["value"]):
                            ioc["type"] = "ip4addr"
                        elif re.match(defs["iocs_types"][1]["regex"], attr["value"]):
                            ioc["type"] = "ip6addr"
                        elif re.match(defs["iocs_types"][2]["regex"], attr["value"]):
                            ioc["type"] = "cidr"
                        elif re.match(defs["iocs_types"][3]["regex"], attr["value"]):
                            ioc["type"] = "domain"
                        elif re.match(defs["iocs_types"][4]["regex"], attr["value"]):
                            ioc["type"] = "sha1cert"
                        elif "alert " in attr["value"][0:6]:
                            ioc["type"] = "snort"
                        else:
                            continue

                        if "Tag" in attr:
                            for tag in attr["Tag"]:
                                # Add a TLP to the IOC if defined in tags.
                                tlp = re.search(
                                    r"^(?:tlp:)(red|green|amber|white)", tag['name'].lower())
                                if tlp:
                                    ioc["tlp"] = tlp.group(1)

                                # Add possible tag (need to match TinyCheck tags)
                                if tag["name"].lower() in [t["tag"] for t in defs["iocs_tags"]]:
                                    ioc["tag"] = tag["name"].lower()
                        yield ioc
                """
