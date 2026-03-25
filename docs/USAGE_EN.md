#  User Guide

How to use **Inbox Debt** to clean your Gmail.

---

##  Login (Production mode)

### With Gmail OAuth

1. Run app: `python app/app.py`
2. Go to `http://localhost:5000`
3. Click **"Connect with Gmail"**
4. Authorize access
5. You're logged in! 

### Demo mode (no Gmail)

No login needed! Simply run:

```bash
export APP_MODE=demo
python app/app.py
```

 See [Demo Mode](./DEMO_MODE_EN.md)

---

##  Homepage

First page shows:

- **Your mode**: "local" (Gmail) or "demo" (sample data)
- **Analyze button**: Start the scan
- **Safelist button**: Manage whitelist

---

##  Analyze emails

### Start analysis

1. Click **"Analyze my inbox"**
2. App connects to Gmail
3. Fetches emails with `List-Unsubscribe` headers
4. Groups them by domain
5. Sorts by count (descending)

### Results

You see a **list of domains** with:

| Info | Example |
|------|---------|
|  Domain | `newsletter.example.com` |
|  Count | `42 emails` |
|  Unsubscribe link |  or  |
|  Actions | View details / Delete |

---

##  Domain details

Click a domain to see:

- **Total emails** count
- **Emails with unsubscribe link**
- **Email preview** (domain, subject, date)
- **Delete option**

---

##  Safelist (Whitelist)

### View safelist

1. Homepage → Click **"Manage safelist"**
2. Or go to `/safelist`

You see protected domains (never deleted).

### Add to safelist

#### Option 1: From analysis

1. Go to `/analyze`
2. Find domain
3. Click **"Add to safelist"**
4. Domain is protected 

#### Option 2: From safelist page

1. Go to `/safelist`
2. Enter domain at bottom
3. Click **"Add"**

### Remove from safelist

From safelist page, click domain to remove it.

---

##  Delete emails

###  Before deleting

1. **Verify domain** → View details
2. **Check not in safelist** → Go to `/safelist`
3. **Double-check** → Necessary!

### Delete

1. From `/analyze`, find domain
2. Click **"Delete"**
3. Confirm 
4. Emails are deleted 

### After deletion

- Domain disappears from list
- `N` emails were deleted
- Confirmation message appears

---

##  Complete workflow

```
1. Gmail login (or demo mode)
     ↓
2. Click "Analyze"
     ↓
3. Fetch emails with List-Unsubscribe
     ↓
4. Results grouped by domain (sorted)
     ↓
5. For each domain:
      View details
      Optional: add to safelist
      If sure: delete
     ↓
6. Emails permanently deleted
```

---

##  Available actions

Per domain, you can:

| Action | Effect | Reversible |
|--------|--------|-----------|
|  View details | Shows info | N/A |
|  Add safelist | Protects |  (remove) |
|  Delete | Deletes from Gmail |  (permanent) |

---

##  Usage tips

###  Best practices

-  **Always verify before deleting**
-  **Use safelist for important domains**
-  **Start small**: test with 1-2 domains
-  **Clean regularly**: once a month
-  **Note your exclusions**

###  Avoid

-  Don't bulk delete without checking
-  Don't delete without viewing details
-  Don't close tab during deletion

---

##  Common issues

###  "No unsubscribe link"

**Reason:** Email doesn't have `List-Unsubscribe` header

**Solution:** Can't auto-unsubscribe. Delete manually or ignore.

###  "Error: Gmail access denied"

**Reason:** Insufficient permissions or token expired

**Solution:**
- Re-login
- Verify OAuth permissions
- Try incognito window

###  "Nothing to analyze"

**Reason:** No emails with `List-Unsubscribe` found

**Solution:**
- Maybe your Gmail is already clean!
- Try search: `has:unsubscribe`

---

##  Need help?

-  [Troubleshooting](./TROUBLESHOOTING_EN.md)
-  [Configuration](./CONFIGURATION_EN.md)
-  [Demo Mode](./DEMO_MODE_EN.md)
