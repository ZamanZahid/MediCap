# AI Medication Scanner

A web application that lets the user:

- Upload 1–3 medication images
- Or enter a medication name manually
- Use Google Gemini to analyze medication information
- Display:
  - Medication name
  - Purpose
  - Ingredients
  - Dosage
  - Side effects
  - Warnings
  - Drug interactions

## Setup

1. Clone the repository
2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Add a Gemini API KEY

```env
API-KEY=YOUR_KEY
```

4. Run

```bash
python app.py
```