# -*- coding: utf-8 -*-
import json
import traceback


def jprint(obj):
    """make beautiful json"""
    return json.dumps(obj, sort_keys=True, indent=4, ensure_ascii=False)


def get_secrets(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        traceback.print_exc()

