# Truth or Dare

A tiny party game: pick **Truth** or **Dare** and get a random challenge that
you'll never see twice (per category) until you've seen them all.

## Project layout

```
truth-or-dare/
├── frontend/               Plain HTML/CSS/JS — host as a static site
│   ├── index.html
│   ├── style.css
│   └── script.js           <-- set API_URL here after deploying the backend
├── backend/                Python, deploy as an AWS Lambda function
│   ├── lambda_function.py  AWS glue (event parsing, DynamoDB scan, CORS)
│   └── challenge_logic.py  Pure "pick a challenge" logic (no AWS deps)
├── data/
│   ├── generate_data.py    Regenerates truths.json / dares.json
│   ├── truths.json         105 unique truths
│   ├── dares.json          105 unique dares
│   └── seed_dynamodb.py    Loads the JSON into DynamoDB
├── tests/
│   └── test_challenge_logic.py   6 unit tests, no AWS needed to run them
└── DEPLOYMENT_GUIDE.md      Full step-by-step AWS free-tier setup
```

## How "no repeats" works

The browser keeps a `localStorage` list of challenge IDs it has already
shown, separately for Truth and Dare. Each request sends that list to the
backend as `?exclude=1,2,7,...`. The backend filters those IDs out before
picking randomly. Once every item in a category has been shown, the next
request naturally has nothing left to exclude against — the backend detects
this, returns `"reset": true`, and the frontend clears that category's
history and starts a fresh cycle.

## Running the tests

```bash
cd tests
python3 -m unittest test_challenge_logic.py -v
```

All 6 tests should pass — they cover: empty deck, exclusion, a full
playthrough with no repeats, the reset-on-exhaustion behavior, a
single-item edge case, and mixed id types.

## Trying the frontend locally (without AWS)

You can preview the UI without deploying anything by temporarily pointing
`API_URL` at a mock, or by running a local Lambda-like server. Simplest
option: just open `frontend/index.html` in a browser to check the layout —
the Truth/Dare buttons won't fetch real data until `API_URL` is set to a
live API Gateway endpoint (see `DEPLOYMENT_GUIDE.md`).

## Deploying to AWS (free tier)

See `DEPLOYMENT_GUIDE.md` for the full walkthrough: DynamoDB tables →
seed data → Lambda → API Gateway → S3 static hosting.
