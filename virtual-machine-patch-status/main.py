#!/usr/bin/env python3
import os
import logging
from azure.identity import ClientSecretCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.subscription import SubscriptionClient
from azure.mgmt.compute import ComputeManagementClient

client_id = os.environ["ARM_CLIENT_ID"]
secret = os.environ["ARM_CLIENT_SECRET"]
tenant = os.environ["TENANT_ID"]


CREDENTIALS = ClientSecretCredential(
    client_id=client_id, client_secret=secret, tenant_id=tenant,
)


def list_subscriptions():
    client = SubscriptionClient(CREDENTIALS)
    # ignore disabled subscriptions
    subs = [
        sub.subscription_id
        for sub in client.subscriptions.list()
        if sub.state == "Enabled"
    ]

    return subs


def list_resource_groups():
    subs = list_subscriptions()
    resource_groups = {}

    for sub in subs:
        resource_group_client = ResourceManagementClient(CREDENTIALS, sub)
        rgs = resource_group_client.resource_groups.list()

        groups = [rg.name for rg in rgs]

        resource_groups[sub] = groups
    return resource_groups


def get_patches(rgs):
    for sub, resources_groups in rgs.items():
        compute_client = ComputeManagementClient(CREDENTIALS, sub)
        for group in resources_groups:
            vms = compute_client.virtual_machines.list(group)
            for vm in vms:
                try:
                    patches = compute_client.virtual_machines.begin_assess_patches(
                        group, vm.name
                    )
                    print(patches.critical_and_security_patch_count)
                except Exception as e:
                    logging.error(f"Unable to get data - {sub}. {e}")


if __name__ == "__main__":
    rgs = list_resource_groups()
    get_patches(rgs)
