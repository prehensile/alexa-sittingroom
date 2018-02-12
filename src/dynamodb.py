import os

import boto3


class DynamoDBHandler(object):
    
    """docstring for DynamoDBHandler"""
    
    def __init__( self ):
        super(DynamoDBHandler, self).__init__()

    def get_dbinstance( self ):
        aws_region = os.environ.get( "AWS_DEFAULT_REGION", "eu-west-1" )
        dynamodb_endpoint = "https://dynamodb.%s.amazonaws.com" % aws_region 
        return boto3.resource(
            'dynamodb',
            region_name=aws_region,
            endpoint_url=dynamodb_endpoint
        )

    def get_table( self ):
        dynamodb = self.get_dbinstance()
        table_name = os.environ.get( "DYNAMODB_TABLE", "henry-sittingroom" )
        return dynamodb.Table( table_name )

    def get_iteration( self ):
        table = self.get_table()
        item = table.get_item(
            Key={ 'CounterId': 0 }
        )
        return item[ 'IterationNumber' ]

    def set_iteration( self, iteration_number ):
        table = self.get_table()
        table.update_item(
            Key={ 'CounterId': 0 },
            UpdateExpression='SET IterationNumber = :val1',
            ExpressionAttributeValues={
                ':val1': iteration_number
            }
        )
