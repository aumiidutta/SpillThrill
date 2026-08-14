"""
Loads truths.json and dares.json into their DynamoDB tables.

Prerequisites:
  1. AWS CLI configured (aws configure) with credentials that can write
     to DynamoDB, OR run this from an environment (e.g. CloudShell) that
     already has AWS credentials.
  2. The two tables already created (see DEPLOYMENT_GUIDE.md), each with
     a partition key named "id" of type String (S).
  3. pip install boto3   (skip this if using AWS CloudShell - preinstalled)

Usage:
  python3 seed_dynamodb.py --region us-east-1
"""
import argparse
import json
import os

import boto3


def load_json(filename):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    with open(path) as f:
        return json.load(f)


def seed_table(dynamodb, table_name, records):
    table = dynamodb.Table(table_name)
    with table.batch_writer(overwrite_by_pkeys=["id"]) as batch:
        for record in records:
            batch.put_item(Item=record)
    print(f"Seeded {len(records)} items into {table_name}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--region", default="us-east-1")
    parser.add_argument("--truths-table", default="TruthOrDare_Truths")
    parser.add_argument("--dares-table", default="TruthOrDare_Dares")
    args = parser.parse_args()

    dynamodb = boto3.resource("dynamodb", region_name=args.region)

    truths = load_json("truths.json")
    dares = load_json("dares.json")

    seed_table(dynamodb, args.truths_table, truths)
    seed_table(dynamodb, args.dares_table, dares)


if __name__ == "__main__":
    main()
