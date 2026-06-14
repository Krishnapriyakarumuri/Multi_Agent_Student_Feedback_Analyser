# UI Overhaul Setup & Testing Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Virtual environment activated
- All dependencies installed from `requirements.txt`

### 1. Start the FastAPI Server

```bash
# In the project root directory
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected Output:**
```
✅ SQLite: Available (built-in)
⚠️ Redis: Not available - Using In-Memory Queue
⚠️ Azure OpenAI: Using demo key
✅ 6 agents registered
📡 API ready at http://localhost:8000
```

### 2. Start the Streamlit Frontend

**In a new terminal:**

```bash
cd frontend
python -m streamlit run app.py --server.port 8501
```

**Streamlit will open automatically at:** http://localhost:8501

---

## 🔐 Authentication System

### Demo Users (Pre-Created)

| Username | Password | Role | Permissions |
|----------|----------|------|-------------|
| `admin` | `admin123` | Admin | Upload, resolve recommendations |
| `viewer` | `viewer123` | Viewer | View-only access |

### Login Page Features
- Clean dark-mode UI
- Demo credentials displayed
- Session-based authentication
- Auto-redirect to dashboard on success

---

## 📋 Feature Walkthrough

### 1. Upload Feedback ➡️ Pipeline Processing

**For Admins Only**

1. Go to **Upload Feedback** page
2. Upload a CSV with columns:
   - **Required**: `feedback_text`
   - **Optional**: `department`, `semester`, `year`, `date`

**Example CSV:**
```csv
feedback_text,department,semester
"Course structure was excellent",Engineering,Spring2024
"Need more practical examples",Business,Spring2024
"Instructor response was slow",Science,Fall2023
```

3. Click **🚀 Deploy Agents & Start Analysis**
4. Auto-redirects to Dashboard to monitor pipeline

### 2. Dashboard Overview 📊

**Available to All Authenticated Users**

**KPI Cards (Row 1):**
- Total Feedbacks
- Positive Sentiment %
- Neutral Sentiment %
- Negative Sentiment %

**KPI Cards (Row 2):**
- 🔴 High Priority Recommendations
- 🟡 Medium Priority Recommendations
- 🟢 Low Priority Recommendations
- ⚠️ Bias Issues Count

**Charts:**
- **Sentiment Distribution**: Donut chart (positive, neutral, negative)
- **Recommendations by Priority**: Bar chart
- **Feedback by Theme & Sentiment**: Grouped bar chart
- **Top Keywords**: Bar chart with frequency

### 3. Recommendations Page ✨ (Core Feature)

**For All Users | Admin Controls Only**

**Display:**
- Unresolved recommendations sorted by priority
- Each recommendation card shows:
  - 📌 Theme name
  - 🔴/🟡/🟢 Priority badge
  - Recommendation text
  - Expected impact
  - Action items (checklist)
  - Fairness note
  - Original feedback preview
  - Creation date

**Filters:**
- Filter by Priority (High/Medium/Low)
- Filter by Theme
- Shows count of filtered results

**Admin Controls:**
- **✅ Mark Resolved** button per recommendation
- Marks as `implemented=true` in database
- Card disappears from active view
- Recommendation stays in database for history

**Viewer:**
- Cannot see "Mark Resolved" button
- See message: "Contact admin to resolve"

**Summary Statistics:**
- Total high priority count
- Total medium priority count
- Total low priority count
- Total active recommendations

### 4. Theme Discovery 🔍

- Browse all discovered themes
- Select theme for deep dive
- View sentiment distribution for that theme
- See top keywords
- Theme-specific sentiment breakdown

### 5. Sentiment Analysis 😊

- Overall sentiment metrics
- Positive/Neutral/Negative percentages
- Sentiment distribution chart
- Per-theme breakdown

### 6. Bias Report ⚖️

- Flagged for Bias count
- Clean Feedback count
- Bias type breakdown table
- Bias severity information

---

## 🛠️ API Endpoints

### Dashboard
```
GET /api/v1/dashboard/summary
```
Returns: KPIs (feedback count, sentiment %, bias issues, recommendations by priority)

```
GET /api/v1/dashboard/charts
```
Returns: Theme×Sentiment matrix, top keywords

### Recommendations
```
GET /api/v1/recommendations/with-meta
```
Returns: All unresolved recommendations with theme info

```
PATCH /api/v1/recommendations/{rec_id}/resolve
```
Marks recommendation as implemented (admin only)

### Reports
```
GET /api/v1/bias/report
```
Returns: Bias flagged items and breakdown

---

## 🧪 Testing Checklist

### 1. Authentication ✅
- [ ] Login with admin/admin123 ✅
- [ ] Login with viewer/viewer123 ✅
- [ ] Invalid credentials show error
- [ ] Logout works and redirects to login
- [ ] Unauthenticated users redirected to login

### 2. Upload & Pipeline ✅
- [ ] Admin can upload CSV
- [ ] Viewer cannot upload (shows error)
- [ ] Pipeline starts and auto-redirects to dashboard
- [ ] Job ID displayed
- [ ] Agent count shown correctly

### 3. Dashboard ✅
- [ ] KPI cards display with correct counts
- [ ] Sentiment chart renders
- [ ] Priority chart renders
- [ ] Theme×Sentiment chart renders
- [ ] Keywords cloud renders
- [ ] Data updates in real-time

### 4. Recommendations Page ✅
- [ ] Recommendations appear after pipeline
- [ ] Priority badges show (🔴🟡🟢)
- [ ] Action items display as list
- [ ] Expected impact shown
- [ ] Fairness notes shown
- [ ] Admin sees "✅ Mark Resolved" button
- [ ] Viewer does NOT see "Mark Resolved" button
- [ ] Clicking "Mark Resolved" resolves recommendation
- [ ] Resolved recommendations disappear from list
- [ ] Summary statistics update
- [ ] Filters work (priority + theme)

### 5. Other Pages ✅
- [ ] Theme Discovery page renders with data
- [ ] Sentiment Analysis page shows metrics
- [ ] Bias Report shows flagged items

---

## 📊 Data Flow

```
1. Admin uploads CSV
   ↓
2. FastAPI receives file and creates job_id
   ↓
3. Orchestrator deploys 6 agents in pipeline:
   - Preprocessing Agent
   - Sentiment Agent
   - Theme Discovery Agent
   - Bias Detection Agent
   - Recommendation Agent
   - Embedding Agent
   ↓
4. Each agent processes feedback and stores results in SQLite
   ↓
5. Recommendation Agent generates recommendations with theme_name
   ↓
6. Dashboard aggregates data from SQLite
   ↓
7. Recommendations Page displays active (unresolved) recommendations
   ↓
8. Admin marks as resolved → implemented=true in database
   ↓
9. Resolved recommendations hidden from active view
```

---

## 🗄️ Database Schema (Key Tables)

### users
```
id (UUID)
username (str, unique)
password_hash (str, SHA256)
role (str: admin/viewer)
created_at (datetime)
```

### recommendations
```
id (UUID)
feedback_id (str)
theme_id (int)
theme_name (str)  ← NEW
recommendation_text (text)
priority (str: high/medium/low)
action_items (JSON)
expected_impact (text)
fairness_note (text)
implemented (bool, default False)  ← Mark resolved
upstream_agents (JSON)
processed_by (str)
created_at (datetime)
```

---

## ⚙️ Environment Variables

Ensure these are in `.env` or `config.py`:

```
GROQ_API_KEY=your_key_or_demo
GROQ_MODEL=mixtral-8x7b-32768
GPT_TEMPERATURE=0.7
GPT_MAX_TOKENS=1000
DATABASE_URL=sqlite:///feedback.db
```

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'groq'"
```bash
pip install groq
```

### "DatabaseError: Recommendation table missing columns"
The database was created before the schema update. Delete `feedback.db` and restart:
```bash
rm feedback.db
python -m uvicorn main:app --reload
```

### Recommendations not appearing
1. Ensure pipeline completed (check Dashboard for job status)
2. Check API endpoint: `http://localhost:8000/api/v1/recommendations/with-meta`
3. Verify recommendations are in SQLite database

### Auth not working
- Ensure `database/auth.py` was created
- Check that User table exists in database
- Verify demo users created on first run

---

## 📝 Example Workflow

### 1. Admin uploads feedback
```
File: feedback.csv
Rows: 100
Status: Processing...
```

### 2. Pipeline completes
```
✅ 6 agents completed processing
Recommendations: 12 high, 8 medium, 5 low
```

### 3. View recommendations
```
🔴 HIGH: Improve placement training
  - Impact: 85% placement success
  - Actions: 5 specific steps
  - Status: Active (unresolved)
```

### 4. Mark as resolved
```
✅ Clicked "Mark Resolved"
Recommendation now implemented=true
Hidden from active list
```

### 5. View resolved history
```
Query database directly to see all recommendations
(implemented=true are hidden from normal view)
```

---

## 🎯 Next Steps

1. Test with your own CSV file
2. Verify all recommendations display correctly
3. Test admin resolve functionality
4. Test viewer read-only access
5. Check database for data persistence
6. Consider adding:
   - Registration system
   - Custom admin dashboard
   - Export recommendations as PDF
   - Email notifications

---

## 📞 Support

For issues or questions, check:
1. Terminal logs from FastAPI server
2. Streamlit browser console (F12)
3. SQLite database directly: `sqlite3 feedback.db`
4. API endpoints in browser: `http://localhost:8000/api/v1/health`

---

**Last Updated:** 2026-06-13
**Version:** 1.0.0
