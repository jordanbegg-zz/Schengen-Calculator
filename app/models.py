from time import time
import datetime

from flask_login import UserMixin
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5
import jwt
import pandas as pd

from app import db, login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(32))
    surname = db.Column(db.String(32))
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    trips = db.relationship("Trip", backref="traveller", lazy="dynamic")

    def __repr__(self):
        return "<User {}>".format(self.email)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode("utf-8")).hexdigest()
        return "https://www.gravatar.com/avatar/{}?d=identicon&s={}".format(
            digest, size
        )

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {"reset_password": self.id, "exp": time() + expires_in},
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        )

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )["reset_password"]
        except:
            return
        return User.query.get(id)

    def get_remaining_days(self, end: datetime.date = datetime.date.today()):
        trips = self.trips.order_by(Trip.start.desc())
        start = min([trip.start for trip in trips])
        index = pd.date_range(start, end).date
        df = pd.DataFrame(index=index)
        df["inSchengen"] = False
        for trip in trips:
            df.loc[trip.start.date() : trip.end.date()] = True
        df["count"] = df["inSchengen"].rolling(window=180, min_periods=0).sum()
        df["remainingDays"] = (90 - df["count"]).astype(int)
        return df.loc[end, "remainingDays"]


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start = db.Column(db.DateTime, index=True)
    end = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))