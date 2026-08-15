import json
import os
import boto3
from challenge_logic import pick_challenge

dynamodb = boto3.resource("dynamodb")

TRUTHS_TABLE = os.environ.get("TRUTHS_TABLE", "Truths")
DARES_TABLE = os.environ.get("DARES_TABLE", "Dares")

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "GET,OPTIONS",
    "Content-Type": "application/json",
}


def _response(status_code, body_dict):
    return {
        "statusCode": status_code,
        "headers": CORS_HEADERS,
        "body": json.dumps(body_dict),
    }


def _scan_all(table):
    """Scan the whole table (tiny table, well within free tier)."""
    items = []
    kwargs = {}
    while True:
        result = table.scan(**kwargs)
        items.extend(result.get("Items", []))
        if "LastEvaluatedKey" not in result:
            break
        kwargs["ExclusiveStartKey"] = result["LastEvaluatedKey"]
    return items


def lambda_handler(event, context):
    # API Gateway HTTP API (payload v2) puts the method here; REST API (v1) elsewhere.
    http_method = (
        event.get("requestContext", {}).get("http", {}).get("method")
        or event.get("httpMethod")
        or "GET"
    )
    if http_method == "OPTIONS":
        return _response(200, {})

    params = event.get("queryStringParameters") or {}
    challenge_type = (params.get("type") or "").lower().strip()
    exclude_param = params.get("exclude", "")

    if challenge_type not in ("truth", "dare"):
        return _response(400, {"error": "Query param 'type' must be 'truth' or 'dare'"})

    table_name = TRUTHS_TABLE if challenge_type == "truth" else DARES_TABLE

    try:
        table = dynamodb.Table(table_name)
        items = _scan_all(table)
    except Exception as exc:  # noqa: BLE001 - surface a clean error to the client
        return _response(500, {"error": f"Could not read {table_name}: {exc}"})

    exclude_ids = [x for x in exclude_param.split(",") if x]

    try:
        chosen, reset_happened = pick_challenge(items, exclude_ids)
    except ValueError as exc:
        return _response(404, {"error": str(exc)})

    return _response(
        200,
        {
            "id": str(chosen.get("id")),
            "text": chosen.get("text"),
            "type": challenge_type,
            "reset": reset_happened,
            "total": len(items),
        },
    )
