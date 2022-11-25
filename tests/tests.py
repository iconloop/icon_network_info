# -*- coding: utf-8 -*-

import os
import sys

import yaml
import unittest
import urllib

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.s3_manager import S3Manager
from lib.base import cPrint


class Tests(unittest.TestCase):

    def test_check_url(self, service:str="MainNet"):
        cPrint("URL Test")
        _url = f"https://networkinfo.solidwallet.io/node_info/{service}/default_configure.yml"
        status_code = urllib.request.urlopen(_url).getcode()
        self.assertTrue(status_code == 200, msg=f"Check url(={_url}).")
        cPrint(" - Completed", "yellow")

    def test_config_data(self, ):
        cPrint("Configure Data Test")
        service_attrs = ['version', 'only_goloop', 'info', 'env']
        _info_file = "info.yml"
        self.assertTrue(os.path.exists(_info_file), msg=f"Check a file(={_info_file}).")
        with open(_info_file, "r") as yml:
            _info = yaml.safe_load(yml)
        _base_file = "icon2/base_configure.yml"
        self.assertTrue(os.path.exists(_base_file), msg=f"Check a file(={_base_file}).")
        with open(_base_file, "r") as yml:
            _base = yaml.safe_load(yml)
        self.assertTrue(_info.get("network_list"), msg=f"Check a attribute(=network_list).")
        for service in _info.get("network_list"):
            for service_attr in service_attrs:
                self.assertNotIn(service_attr, [_info.keys()], msg=f"Check a service name(e.g., MainNet).")
            for env_attr in _info[service]['env'].keys():
                self.assertNotIn(env_attr, [_base['reference']['env'].keys()],
                                 msg=f"Attribute is not found(={env_attr}. (in the {_base_file}.reference.env)")
                if env_attr.lower() == "iiss":
                    continue
                self.assertEqual(type(_info[service]['env'][env_attr]).__name__, _base['reference']['env'][env_attr]['type'],
                                 msg=f"Check a type(={_info_file}.{service}.env.{env_attr}, "
                                     f"{_base_file}.reference.env.{env_attr}.type).")
        cPrint(" - Completed", "yellow")

    def test_aws_connection(self, ):
        cPrint("AWS Connection Test")
        _info_file = "info.yml"
        self.assertTrue(os.path.exists(_info_file), msg=f"")
        with open(_info_file, "r") as yml:
            _info = yaml.safe_load(yml)
        for env_attr in _info.get('git_env').keys():
            self.assertTrue(os.getenv(env_attr), msg=f"Check the os env(export) for the AWS connection")
        self.assertRaises(
            Exception,
            S3Manager.aws_client(
                's3',
                os.getenv('aws_access_key_id'),
                os.getenv('aws_secret_access_key'),
                os.getenv('aws_default_region')
            ),
            msg="AWS connection failed."
        )
        cPrint(" - Completed", "yellow")

    def run(self, ):
        self.test_check_url()
        self.test_config_data()
        self.test_aws_connection()


if __name__ == "__main__":
    TS = Tests()
    TS.run()