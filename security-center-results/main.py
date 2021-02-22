#!/usr/bin/env python3
import os
import logging
from azure.identity import ClientSecretCredential
from azure.mgmt.security import SecurityCenter
from azure.mgmt.subscription import SubscriptionClient
from collections import Counter

client_id = os.environ["ARM_CLIENT_ID"]
secret = os.environ["ARM_CLIENT_SECRET"]
tenant = os.environ["TENANT_ID"]

CREDENTIALS = ClientSecretCredential(
    client_id=client_id, client_secret=secret, tenant_id=tenant,
)

client = SubscriptionClient(CREDENTIALS)

compliance = []
alerts = []


for sub in client.subscriptions.list():
    sub_id = f"/subscriptions/{sub.subscription_id}"

    if sub.state == "Enabled":
        try:
            client = SecurityCenter(
                CREDENTIALS, sub.subscription_id, asc_location="westeurope"
            )
            for al in client.alerts.list():
                alerts.append(f"{al.severity}-{al.alert_display_name}")

            for assessment in client.assessments.list(scope=sub_id):
                if assessment.status.code == "Unhealthy":
                    compliance.append(assessment.display_name)
        except Exception as e:
            logging.error(f"Unable to get data - {sub_id}. {e}")
print("Alert results:")
for i in Counter(alerts).most_common():
    print(i)

print("Compliance results:")
for i in Counter(compliance).most_common():
    print(i)
