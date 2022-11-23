from decimal import Decimal

import boto3
from sklearn.datasets import make_moons

if __name__ == "__main__":
    dynamodb = boto3.resource("dynamodb")

    # Create DynamoDB table:
    try:
        table = dynamodb.create_table(
            TableName="Point",
            KeySchema=[
                {
                    'AttributeName': 'x',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'y',
                    'KeyType': 'RANGE'
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'x',
                    'AttributeType': 'N'
                },
                {
                    'AttributeName': 'y',
                    'AttributeType': 'N'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
    except boto3.client("dynamodb").exceptions.ResourceInUseException as e:
        table = dynamodb.Table("Point")

    # Write DynamoDB with orginal data:
    points, classes = make_moons(50, noise=0.3, random_state=0)

    with table.batch_writer() as batch:
        for point, cls in zip(points, classes):
            batch.put_item(
                Item={
                    "x": Decimal(str(point[0])),
                    "y": Decimal(str(point[1])),
                    "class": Decimal(str(cls)),
                    "origin": "original"
                }
            )


