#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify, Response, request
from app.decorators import require_header_token, require_get_token
from app.classes.octi import OCTI

import json

octi_bp = Blueprint("octi", __name__)
octi = OCTI()


@octi_bp.route('/add', methods=['POST'])
@require_header_token
def add_instance():
    """
        Parse and add a OpenCTI instance to the database.
        :return: status of the operation in JSON
    """
    data = json.loads(request.data)
    res = octi.add_instance(data["data"]["instance"])
    return jsonify(res)


@octi_bp.route('/delete/<octi_id>', methods=['GET'])
@require_header_token
def delete_instance(octi_id):
    """
        Delete a OpenCTI instance by its id to the database.
        :return: status of the operation in JSON
    """
    res = octi.delete_instance(octi_id)
    return jsonify(res)


@octi_bp.route('/get_all', methods=['GET'])
@require_header_token
def get_all():
    """
        Retreive a list of all OpenCTI instances.
        :return: list of OpenCTI instances in JSON.
    """
    res = octi.get_instances()
    return jsonify({"results": [i for i in res]})
