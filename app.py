from flask import Flask, abort, flash, redirect, render_template, request, url_for

from models import Duck, Loan, Member, db


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SECRET_KEY"] = "dev"
    db.init_app(app)

    with app.app_context():
        db.create_all()
        seed(db)

    register_routes(app)
    return app


def seed(db):
    members = [Member(name=n) for n in ("Alice", "Bao", "Carmen")]
    ducks = [Duck() for _ in range(5)]
    db.session.add_all(members + ducks)
    db.session.commit()

    # One duck already out on loan, so the dashboard has something to show.
    Loan.start(members[0], ducks[0])
    db.session.commit()


def register_routes(app):
    @app.route("/")
    def index():
        ducks = Duck.query.order_by(Duck.duck_id).all()
        return render_template("index.html", ducks=ducks)

    @app.route("/borrow", methods=["GET", "POST"])
    def borrow():
        members = Member.query.order_by(Member.name).all()
        available_ducks = [d for d in Duck.query.order_by(Duck.duck_id) if d.active_loan is None]

        if request.method == "POST":
            member = Member.query.get(request.form.get("member_id", type=int))
            duck = Duck.query.get(request.form.get("duck_id", type=int))
            if member is None or duck is None:
                abort(400)
            try:
                Loan.start(member, duck)
                db.session.commit()
            except ValueError as exc:
                flash(str(exc))
                return redirect(url_for("borrow"))
            flash(f"{member.name} borrowed Duck {duck.duck_id}. Due back in 7 days.")
            return redirect(url_for("index"))

        return render_template("borrow.html", members=members, ducks=available_ducks)

    @app.route("/members", methods=["GET", "POST"])
    def members():
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            if not name:
                flash("Member name is required.")
                return redirect(url_for("members"))
            db.session.add(Member(name=name))
            db.session.commit()
            flash(f"Added member {name}.")
            return redirect(url_for("members"))

        all_members = Member.query.order_by(Member.name).all()
        return render_template("members.html", members=all_members)

    @app.route("/members/<int:member_id>/delete", methods=["POST"])
    def delete_member(member_id):
        member = Member.query.get_or_404(member_id)
        if member.has_active_loan:
            flash(f"Cannot remove {member.name}: they still have a duck on loan.")
            return redirect(url_for("members"))
        db.session.delete(member)
        db.session.commit()
        flash(f"Removed member {member.name}.")
        return redirect(url_for("members"))

    @app.route("/return/<int:loan_id>", methods=["POST"])
    def return_duck(loan_id):
        loan = Loan.query.get_or_404(loan_id)
        if loan.returned_date is not None:
            abort(400)
        from datetime import date

        loan.returned_date = date.today()
        db.session.commit()
        flash(f"Duck {loan.duck_id} returned by {loan.member.name}.")
        return redirect(url_for("index"))


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
