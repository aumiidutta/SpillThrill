# Deploying SpillThrill on AWS





## Part 1 — Create the DynamoDB tables

1. Go to the **DynamoDB** console → **Tables** → **Create table**.
2. Table 1:

   * Table name: `Truths`
   * Partition key: `id`, type **String**
   * Table settings: leave "Default settings" (on-demand capacity is free-tier friendly for this scale)
   * Click **Create table**.
3. Repeat for Table 2:

   * Table name: `Dares`
   * Partition key: `id`, type **String**





## Part 2 — Seed the tables with the 100+ challenges

Easiest path: use **AWS CloudShell** (top-right icon in the AWS Console) — it already has Python + boto3 and your console credentials.

1. Open CloudShell.
2. Upload `data/truths.json`, `data/dares.json`, and `data/seed\_dynamodb.py` (CloudShell → Actions → Upload file).
3. Run:

&#x20;  ```bash
pip install boto3 --quiet   # usually already installed
python3 seed\_dynamodb.py --region us-east-1

```

4. You should see:

\&#x20;  ```
   Seeded 105 items into TruthOrDare\_Truths
   Seeded 105 items into TruthOrDare\_Dares
   ```

5. Spot-check in the DynamoDB console → table → **Explore table items**.





## Part 3 — Create the Lambda function

1. Go to the **Lambda** console → **Create function**.
2. Choose **Author from scratch**.

   * Function name: `TruthOrDareFunction`
   * Runtime: **Python 3.12**
   * Architecture: `x86\_64`
3. Click **Create function**.
4. In the **Code** tab, delete the placeholder code and:

   * Create a file `challenge\_logic.py` and paste the contents of `backend/challenge\_logic.py`.
   * Replace `lambda\_function.py`'s contents with `backend/lambda\_function.py`.
   * Click **Deploy**.
5. Go to **Configuration → Environment variables** → **Edit** → **Add environment variable**:

   * `TRUTHS\_TABLE` = `TruthOrDare\_Truths`
   * `DARES\_TABLE` = `TruthOrDare\_Dares`
   * Save.
6. Go to **Configuration → Permissions**. Click the execution role name (opens IAM).

   * Click **Add permissions → Attach policies**.
   * Attach `AmazonDynamoDBReadOnlyAccess` (sufficient — the app only reads).
   * Save.
7. (Optional but recommended) **Configuration → General configuration → Edit**: set Timeout to `10 sec` (default 3s is usually enough, but this gives headroom).





## Part 4 — Create the API Gateway (HTTP API)

1. Go to the **API Gateway** console → **Create API** → **HTTP API** → **Build**.
2. **Integrations**: Add integration → Lambda → select `TruthOrDareFunction`.
3. **Configure routes**:

   * Method: `GET`
   * Resource path: `/challenge`
   * Integration target: `TruthOrDareFunction`
4. **Configure stages**: keep the default `$default` auto-deploy stage.
5. Click **Create**.
6. On the API's **Details** page, copy the **Invoke URL** (looks like `https://abc123xyz.execute-api.us-east-1.amazonaws.com`). Your full endpoint will be:

&#x20;  ```
https://abc123xyz.execute-api.us-east-1.amazonaws.com/challenge

```

7. \*\*Enable CORS\*\* (needed since the frontend on S3 is a different origin):

   \* Left menu → \*\*CORS\*\* → \*\*Configure\*\*.
   \* Access-Control-Allow-Origin: `\*` (or your S3 website URL once you have it, for tighter security)
   \* Access-Control-Allow-Methods: `GET, OPTIONS`
   \* Access-Control-Allow-Headers: `Content-Type`
   \* Save.
8. Test it directly in your browser:

\&#x20;  ```
   https://abc123xyz.execute-api.us-east-1.amazonaws.com/challenge?type=truth
   ```

You should get back JSON like:

&#x20;  ```json
{"id": "42", "text": "What's your biggest regret?", "type": "truth", "reset": false, "total": 105}

```





## Part 5 — Wire the frontend to your API and host it on S3

1. Open `frontend/script.js` and set:

\&#x20;  ```js
   const API\_URL = "https://abc123xyz.execute-api.us-east-1.amazonaws.com/challenge";
   ```

2. Go to the **S3** console → **Create bucket**.

   * Bucket name: something globally unique, e.g. `truth-or-dare-yourname`
   * **Uncheck** "Block all public access" (a static website needs public read access) and acknowledge the warning.
   * Create bucket.
3. Open the bucket → **Properties** tab → scroll to **Static website hosting** → **Edit**.

   * Enable it.
   * Index document: `index.html`
   * Save.
4. Go to the **Permissions** tab → **Bucket policy** → paste (replace `BUCKET\_NAME`):

&#x20;  ```json
{
"Version": "2012-10-17",
"Statement": \[
{
"Sid": "PublicReadGetObject",
"Effect": "Allow",
"Principal": "\*",
"Action": "s3:GetObject",
"Resource": "arn:aws:s3:::BUCKET\_NAME/\*"
}
]
}

```

5. Go to the \*\*Objects\*\* tab → \*\*Upload\*\* → add `index.html`, `style.css`, `script.js` (with the API\_URL already filled in) → \*\*Upload\*\*.
6. Back in \*\*Properties → Static website hosting\*\*, copy the \*\*Bucket website endpoint\*\* URL — that's your live app!





## Part 6 — Play!

Open the S3 website URL on your phone and on a desktop browser — the layout adapts to both. Tap \*\*Truth\*\* or \*\*Dare\*\*, and the same challenge won't show up again until every entry in that category has been seen once.




