# Truth or Dare



## About

A tiny party game: pick **Truth** or **Dare** and get a random challenge.



## Project layout

```
truth-or-dare/
├── frontend/               
│   ├── index.html
│   ├── style.css
│   └── script.js           
├── backend/                
│   ├── lambda\\\\\\\\\\\\\\\_function.py  
│   └── challenge\\\\\\\\\\\\\\\_logic.py  
├── data/
│   ├── generate\\\\\\\\\\\\\\\_data.py    
│   ├── truths.json         
│   ├── dares.json          
│   └── seed\\\\\\\\\\\\\\\_dynamodb.py    
├── tests/
│   └── test\\\\\\\\\\\\\\\_challenge\\\\\\\\\\\\\\\_logic.py
└── SETUP\\\\\\\\\\\\\\\_GUIDE.md      
```

## How "no repeats" works

The browser keeps a `localStorage` list of challenge IDs it has already
shown, separately for Truth and Dare. Each request sends that list to the
backend as `?exclude=1,2,7,...`. The backend filters those IDs out before
picking randomly. Once every item in a category has been shown, the next
request naturally has nothing left to exclude against — the backend detects
this, returns `"reset": true`, and the frontend clears that category's
history and starts a fresh cycle.



## Trying the frontend locally (without AWS)

You can preview the UI without deploying anything by temporarily pointing
`API\\\\\\\\\\\\\\\_URL` at a mock, or by running a local Lambda-like server. Simplest
option: just open `frontend/index.html` in a browser to check the layout —
the Truth/Dare buttons won't fetch real data until `API\\\\\\\\\\\\\\\_URL` is set to a
live API Gateway endpoint (see `DEPLOYMENT\\\\\\\\\\\\\\\_GUIDE.md`).



## Deploying to AWS

See `DEPLOYMENT\\\\\\\\\\\\\\\_GUIDE.md` for the full walkthrough: DynamoDB tables →
seed data → Lambda → API Gateway → S3 static hosting.

