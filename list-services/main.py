#!/usr/bin/env python3
import os
import logging
from azure.identity import ClientSecretCredential
from azure.mgmt.subscription import SubscriptionClient
from azure.mgmt.resource import ResourceManagementClient
from collections import Counter

client_id = os.environ["ARM_CLIENT_ID"]
secret = os.environ["ARM_CLIENT_SECRET"]
tenant = os.environ["TENANT_ID"]


CREDENTIALS = ClientSecretCredential(
    client_id=client_id, client_secret=secret, tenant_id=tenant,
)

client = SubscriptionClient(CREDENTIALS)

az_services =[]

for sub in client.subscriptions.list():
    if sub.state == "Enabled":
        try:
            resource_group_client = ResourceManagementClient(CREDENTIALS, sub.subscription_id)

            resources = resource_group_client.resources.list()
            for i in resources:
                if "databases/master" not in i.id:
                    az_services.append(i.type.lower())
        except Exception as e:
            logging.error(f"Unable to get data - {sub.subscription_id}. {e}")


print(len(az_services))

for i in Counter(az_services).most_common():
    print(i)