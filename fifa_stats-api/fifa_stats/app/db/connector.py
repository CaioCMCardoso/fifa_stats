import boto3

from fifa_stats.app.settings.configuration import Configuration


class DynamoConnector:
    def __init__(self):
        cfg = Configuration.instance()

        self.region = cfg.AWS_REGION
        self.table_name = cfg.DYNAMO_TABLE_NAME
        self.team_id = cfg.DYNAMO_TEAM_ID

        self._resource = boto3.resource("dynamodb", region_name=self.region)
        self._table = self._resource.Table(self.table_name)

    @property
    def table(self):
        return self._table
