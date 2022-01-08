from time import time
import datetime

from flask_login import UserMixin
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5
import jwt
import pandas as pd
from typing import Optional, Union

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

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode("utf-8")).hexdigest()
        return "https://www.gravatar.com/avatar/{}?d=identicon&s={}".format(
            digest, size
        )

    def get_reset_password_token(self, expires_in: Optional[int] = 600):
        return jwt.encode(
            {"reset_password": self.id, "exp": time() + expires_in},
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        )

    @staticmethod
    def verify_reset_password_token(token: str):
        try:
            id = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )["reset_password"]
        except:
            return
        return User.query.get(id)

    def get_remaining_days(
        self, end: Optional[datetime.date] = datetime.date.today()
    ) -> pd.Series:
        trips = self.trips.order_by(Trip.start.desc())
        if trips.count() == 0:
            return pd.Series(index=[end], data=[90])
        start = min(trip.start for trip in trips)
        index = pd.date_range(start, end).date
        df = pd.DataFrame(index=index)
        df["inSchengen"] = False
        for trip in trips:
            df.loc[trip.start : trip.end] = True
        df["count"] = df["inSchengen"].rolling(window=180, min_periods=0).sum()
        df["remainingDays"] = (90 - df["count"]).astype(int)
        return df["remainingDays"]


@login.user_loader
def load_user(id: Union[str, float, int]):
    return User.query.get(int(id))


class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start = db.Column(db.Date, index=True)
    end = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
