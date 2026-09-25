# Duck Lending Library (prototype)

A small Flask app implementing the core user story: a member borrows a duck,
keeps it for up to 7 days, and returns it. Staff can see who currently holds
which ducks from the dashboard.

## Run it

```
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5000/

Data lives in an in-memory SQLite database, seeded with 3 members and 5
ducks (one already on loan) on startup, and is reset every time the app
restarts.

## Scope

Matches the trimmed class diagram: `Member`, `Duck`, `Loan`. No
authentication, no external services. Borrowing a duck that's already on
loan is rejected (see `Loan.start` in `models.py`); a loan becomes
"Overdue" on the dashboard once its due date has passed without a return.
