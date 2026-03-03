import os

import boto3


class DynamoConnector:
    def __init__(self):
        self.region = os.getenv("AWS_REGION", "sa-east-1")
        self.table_name = os.getenv("DYNAMO_TABLE_NAME", "fifa_players")
        self.team_id = os.getenv("DYNAMO_TEAM_ID", "Rocambole")

        self._resource = boto3.resource("dynamodb", region_name=self.region)
        self._table = self._resource.Table(self.table_name)

    @property
    def table(self):
        return self._table
