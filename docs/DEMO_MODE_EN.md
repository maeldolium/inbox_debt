#  Demo Mode - Complete Guide

The **demo mode** lets you test Inbox Debt **without Gmail** using sample data.

---

##  Run demo mode

### Locally

```bash
# Activate venv
source venv/bin/activate  # Linux/macOS
# or
.\venv\Scripts\Activate.ps1  # Windows

# Run
export APP_MODE=demo
python app/app.py
```

Open `http://localhost:5000`

### Online

 [https://inboxdebt-production.up.railway.app/](https://inboxdebt-production.up.railway.app/)

### With Docker

```bash
docker run -p 8080:8080 -e APP_MODE=demo inbox_debt:latest
```

Open `http://localhost:8080`

---

##  Sample Data (Mock Data)

Demo mode loads data from `app/mock/mock_analysis.json`.

### Data structure

```json
{
  "gmail.com": {
    "count": 45,
    "unsubscribe_links": ["https://mail.google.com/unsubscribe"],
    "message_ids": ["msg_id_1", "msg_id_2", ...]
  },
  "newsletter.example.com": {
    "count": 23,
    "unsubscribe_links": ["https://example.com/unsub"]
  }
}
```

**Fields:**
- `count` : number of emails from this domain
- `unsubscribe_links` : list of unsubscribe links
- `message_ids` : email IDs (for simulation)

---

##  Demo features

###  What you can do

| Feature | Demo | Notes |
|---------|------|-------|
|  See homepage |  | Index page |
|  Analyze data |  | Loads mock data |
|  See domain details |  | Route `/domain/<domain>` |
|  Manage safelist |  | In-memory simulation |
|  Delete (simulated) |  | No actual Gmail call |
|  Complete interface |  | Normal HTML/CSS/JS |

###  What you can't do

| Feature | Reason |
|---------|--------|
|  Gmail login | No OAuth in demo |
|  Access real Gmail | APP_MODE=demo skips API |
|  Persist data | Data resets on refresh |
|  Real unsubscribe | Links don't work (no Gmail call) |

---

##  Test features

### 1⃣ Homepage

```
http://localhost:5000/
```

Shows simple page with demo mode indicator.

### 2⃣ Analyze emails

```
http://localhost:5000/analyze
```

Loads and displays sample data grouped by domain.

### 3⃣ See domain details

Click a domain from `/analyze` or go to:

```
http://localhost:5000/domain/gmail.com
```

Shows: email count, unsubscribe links, etc.

### 4⃣ Manage safelist

```
http://localhost:5000/safelist
```

- View whitelisted domains
- Simulate adding a domain
- In demo mode, no disk persistence

### 5⃣ Delete (simulated)

From `/analyze`, click "Delete" button for a domain.

Receives message: `[DEMO] N simulated emails deleted from example.com`

In-memory data updated, but nothing affects Gmail.

---

##  Tests in demo mode

A suite of **11 pytest tests** validates demo mode:

```bash
# Run all tests
pytest tests/ -v

# Part of suite:
#  test_index_responds_200
#  test_analyze_get_responds_200
#  test_domain_detail_with_valid_domain
#  test_safelist_view_responds_200
#  test_mock_data_loads
```

---

##  Demo mode source files

```
app/
 app.py                      # Main logic
 config/
    settings.py             # APP_MODE=demo
 mock/
    mock_analysis.json      # Sample data
 templates/
    index.html
    results.html            # Shows analysis
    domain.html             # Domain details
    safelist.html           # Safelist management
 gmail_api/
     fetch_emails.py         # Demo returns mock data
```

---

##  Modify sample data

To test with different data, edit `app/mock/mock_analysis.json`:

```json
{
  "example.com": {
    "count": 100,
    "unsubscribe_links": ["https://example.com/unsubscribe"],
    "message_ids": ["id1", "id2", "id3"]
  },
  "test.io": {
    "count": 50,
    "unsubscribe_links": [],
    "message_ids": []
  }
}
```

Restart the app, new data loads! 

---

##  Demo → Production

To switch to production with real Gmail:

1. Authenticate with Google OAuth
2. Change `APP_MODE=local`
3. Provide secure `FLASK_SECRET_KEY`
4. Run `python app/app.py`

 See [Configuration](./CONFIGURATION_EN.md)

---

##  Demo mode troubleshooting

###  Blank page

**Solution:**
```bash
# Verify templates exist
ls app/templates/

# Verify APP_MODE
export APP_MODE=demo
python app/app.py
```

###  Sample data won't load

**Solution:**
```bash
# Check file
cat app/mock/mock_analysis.json

# Validate JSON is valid
python -c "import json; json.load(open('app/mock/mock_analysis.json'))"
```

###  Demo mode not detected

**Solution:**
```bash
# Force it
export APP_MODE=demo
# No spaces around =
APP_MODE=demo python app/app.py
```

---

##  Next steps

-  [User Guide](./USAGE_EN.md) - How to use all features
-  [Development Guide](./DEVELOPMENT_EN.md) - Modify and contribute
