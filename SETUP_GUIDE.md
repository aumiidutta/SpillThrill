## Create the DynamoDB tables

1. Go to the **DynamoDB** console → **Tables** → **Create table**.
2. Table 1:
   - Table name: `Truths`
   - Partition key: `id`, type **String**
   - Table settings: leave "Default settings" (on-demand capacity is free-tier friendly for this scale)
   - Click **Create table**.
3. Repeat for Table 2:
   - Table name: `Dares`
   - Partition key: `id`, type **String**


## Seed the tables using AWS Lambda console

1. Go to the **Lambda** console → **Create function** → Author from scratch.
   - Name: `TruthOrDareSeeder`
   - Runtime: **Python 3.12**
   - Click **Create function**.
2. Delete the placeholder code in `lambda_function.py` and paste in the
   entire contents of `backend/seed_lambda_function.py` (it already has
   all 105 truths + 105 dares embedded, so there's nothing else to upload).
   Click **Deploy**.
3. Give this function's role write access to DynamoDB:
   - **Configuration → Permissions** → click the execution role link (opens IAM in a new tab).
   - **Add permissions → Attach policies** → search for and attach `AmazonDynamoDBFullAccess`.
   - Save.
4. Go to the **Test** tab → **Create new event** → name it anything (e.g. `seedOnce`) → leave the JSON body as `{}` → **Save** → **Test**.
5. Check the execution result panel — you should see:
```json
{
   "message": "Seeding complete",
   "truths_loaded": 105,
   "dares_loaded": 105
}
```
6. Spot-check in the DynamoDB console → table → **Explore table items**.


## Create the Lambda function

1. Go to the **Lambda** console → **Create function**.
2. Choose **Author from scratch**.
   - Function name: `TruthOrDareFunction`
   - Runtime: **Python 3.12**
   - Architecture: `x86_64`
3. Click **Create function**.
4. In the **Code** tab, delete the placeholder code and:
   - Create a file `challenge_logic.py` and paste the contents of `backend/challenge_logic.py`.
   - Replace `lambda_function.py`'s contents with `backend/lambda_function.py`.
   - Click **Deploy**.
5. Go to **Configuration → Environment variables** → **Edit** → **Add environment variable**:
   - `TRUTHS_TABLE` = `Truths`
   - `DARES_TABLE` = `Dares`
   - Save.
6. Go to **Configuration → Permissions**. Click the execution role name (opens IAM).
   - Click **Add permissions → Attach policies**.
   - Attach `AmazonDynamoDBReadOnlyAccess` (sufficient — the app only reads).
   - Save.


## Create the API Gateway (HTTP API)

1. Go to the **API Gateway** console → **Create API** → **HTTP API** → **Build**. Name the API as **TruthOrDareAPI**.
2. **Integrations**: Add integration → Lambda → select `TruthOrDareFunction`.
3. **Configure routes**:
   - Method: `GET`
   - Resource path: `/challenge`
   - Integration target: `TruthOrDareFunction`
4. **Configure stages**: keep the default `$default` auto-deploy stage.
5. Click **Create**.
6. On the API's **Details** page, copy the **Invoke URL** (looks like `https://abc123xyz.execute-api.us-east-1.amazonaws.com`). Your full endpoint will be:
```
https://abc123xyz.execute-api.us-east-1.amazonaws.com/challenge
```
7. **Enable CORS** (needed since the frontend on S3 is a different origin):
   - Left menu → **CORS** → **Configure**.
   - Access-Control-Allow-Origin: `*` (or your S3 website URL once you have it, for tighter security)
   - Access-Control-Allow-Methods: `GET, OPTIONS`
   - Access-Control-Allow-Headers: `Content-Type`
   - Save.

8. Test it directly in your browser:
```
https://abc123xyz.execute-api.us-east-1.amazonaws.com/challenge?type=truth
```
   You should get back JSON like:
```json
{"id": "42", "text": "What's your biggest regret?", "type": "truth", "reset": false, "total": 105}
```


## Upload the frontend and host using S3 bucket

1. Open `frontend/script.js` and set:
```js
const API_URL = "https://abc123xyz.execute-api.us-east-1.amazonaws.com/challenge";
```
2. Go to the **S3** console → **Create bucket**.
   - Bucket name: something globally unique, e.g. `truth-or-dare-yourname`
   - **Uncheck** "Block all public access" (a static website needs public read access) and acknowledge the warning.
   - Create bucket.
3. Open the bucket → **Properties** tab → scroll to **Static website hosting** → **Edit**.
   - Enable it.
   - Index document: `index.html`
   - Save.
4. Go to the **Permissions** tab → **Bucket policy** → paste (replace `BUCKET_NAME`):
```json
{
   "Version": "2012-10-17",
   "Statement": [
      {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::BUCKET_NAME/*"
      }
   ]
}
```
5. Go to the **Objects** tab → **Upload** → add `index.html`, `style.css`, `script.js` (with the API_URL already filled in) → **Upload**.
6. Back in **Properties → Static website hosting**, copy the **Bucket website endpoint** URL — that's your live app!


## Play the game!

Open the S3 website URL on your phone and on a desktop browser — the layout adapts to both. Tap **Truth** or **Dare**, and the same challenge won't show up again until every entry in that category has been seen once.


## Troubleshooting

- **CORS error in the browser console** → double-check step 4.7 (CORS config on the API) and that `script.js` points to the exact invoke URL including `/challenge`.
- **"Could not read TruthOrDare_Truths"** → check the Lambda's IAM role has `AmazonDynamoDBReadOnlyAccess`, and that the table names match the environment variables exactly.
- **Empty response / 404** → confirm the seeding script ran successfully (Part 2) and the tables actually contain items.
- **Costs** → all four services stay within free tier for casual/personal use. DynamoDB and Lambda's free tiers are permanent; S3 and API Gateway's free tiers last 12 months from account creation — after that, traffic at this scale still costs cents, not dollars.