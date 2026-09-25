from datetime import date, timedelta

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

LOAN_PERIOD_DAYS = 7


class Member(db.Model):
    __tablename__ = "member"

    member_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    loans = db.relationship("Loan", back_populates="member", cascade="all, delete-orphan")

    @property
    def has_active_loan(self):
        return any(loan.returned_date is None for loan in self.loans)


class Duck(db.Model):
    __tablename__ = "duck"

    duck_id = db.Column(db.Integer, primary_key=True)

    loans = db.relationship("Loan", back_populates="duck")

    @property
    def active_loan(self):
        for loan in self.loans:
            if loan.returned_date is None:
                return loan
        return None


class Loan(db.Model):
    __tablename__ = "loan"

    loan_id = db.Column(db.Integer, primary_key=True)
    borrowed_date = db.Column(db.Date, nullable=False, default=date.today)
    due_date = db.Column(db.Date, nullable=False)
    returned_date = db.Column(db.Date, nullable=True)

    member_id = db.Column(db.Integer, db.ForeignKey("member.member_id"), nullable=False)
    duck_id = db.Column(db.Integer, db.ForeignKey("duck.duck_id"), nullable=False)

    member = db.relationship("Member", back_populates="loans")
    duck = db.relationship("Duck", back_populates="loans")

    @property
    def is_overdue(self):
        return self.returned_date is None and date.today() > self.due_date

    @classmethod
    def start(cls, member, duck):
        """Create a new loan for a duck that is not currently on loan.

        Raises ValueError if the duck is already out, enforcing the
        acceptance criterion that a duck cannot have two open loans.
        """
        if duck.active_loan is not None:
            raise ValueError(f"Duck {duck.duck_id} is already on loan.")
        today = date.today()
        loan = cls(
            member=member,
            duck=duck,
            borrowed_date=today,
            due_date=today + timedelta(days=LOAN_PERIOD_DAYS),
        )
        db.session.add(loan)
        return loan
