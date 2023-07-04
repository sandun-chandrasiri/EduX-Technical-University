"""
@author: Sandun Chandrasiri
"""

import boto3
import key_config as keys

dynamodb = boto3.resource(
    'dynamodb',
    region_name           = keys.REGION_NAME,
)
