import os

import flask
import pydantic
from flask import jsonify, request
from flask.views import MethodView
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import IntegrityError

import schema
from models import Session, User, Ads

app = flask.Flask("app")
bcrypt = Bcrypt(app)


def hash_password(password: str):
    password = password.encode()
    hashed_password = bcrypt.generate_password_hash(password)
    hashed_password = hashed_password.decode()
    return hashed_password


def check_password(password: str, hashed_password: str):
    password = password.encode()
    hashed_password = hashed_password.encode()
    return bcrypt.check_password_hash(hashed_password, password)


class HttpError(Exception):

    def __init__(self, status_code: int, error_message: dict | str | list):
        self.status_code = status_code
        self.error_message = error_message


@app.errorhandler(HttpError)
def error_handler(er: HttpError):
    response = jsonify({"error": er.error_message})
    response.status_code = er.status_code
    return response


@app.before_request
def before_request():
    session = Session()
    request.session = session


@app.after_request
def after_request(http_response: flask.Response):
    request.session.close()
    return http_response


def validate(
    json_data: dict, schema_cls: type[schema.UpdateUser] | type[schema.CreateUser] |
                                 type[schema.UpdateAd] |   type[schema.CreateAd]
):
    try:
        return schema_cls(**json_data).dict(exclude_unset=True)
    except pydantic.ValidationError as err:
        errors = err.errors()
        for error in errors:
            error.pop("ctx", None)
        raise HttpError(400, errors)


def get_user_by_id(user_id):
    user = request.session.get(User, user_id)
    if user is None:
        raise HttpError(404, "user not found")
    return user


def add_user(user):
    request.session.add(user)
    try:
        request.session.commit()
    except IntegrityError:
        raise HttpError(409, "user already exists")
    return user


def get_ad_by_id(ad_id):
    ad = request.session.get(Ads, ad_id)
    if ad is None:
        raise HttpError(404, "ad not found")
    return ad


def add_ads(ad):
    request.session.add(ad)
    try:
        request.session.commit()
    except IntegrityError:
        raise HttpError(409, "ads already exists")
    return ad


class AdsView(MethodView):
    def get(self, ad_id):

        ad = get_ad_by_id(ad_id)
        return jsonify(ad.dict)

    def post(self):
        json_data = validate(request.json, schema.CreateAd)
        ad = Ads(**json_data)
        ad = add_ads(ad)
        return jsonify(ad.dict)

    def patch(self, ad_id: int):
        json_data = validate(request.json, schema.UpdateAd)
        ad = get_ad_by_id(ad_id)
        for field, value in json_data.items():
            setattr(ad, field, value)
        ad = add_ads(ad)
        return jsonify(ad.dict)

    def delete(self, ad_id: int):

        ad = get_ad_by_id(ad_id)
        request.session.delete(ad)
        request.session.commit()
        return jsonify({"status": "deleted"})


class UserView(MethodView):
    def get(self, user_id):

        user = get_user_by_id(user_id)
        return jsonify(user.dict)

    def post(self):
        json_data = validate(request.json, schema.CreateUser)
        json_data["password"] = hash_password(json_data["password"])
        user = User(**json_data)
        user = add_user(user)
        return jsonify(user.dict)

    def patch(self, user_id: int):
        json_data = validate(request.json, schema.UpdateUser)
        if "password" in json_data:
            json_data["password"] = hash_password(json_data["password"])
        user = get_user_by_id(user_id)
        for field, value in json_data.items():
            setattr(user, field, value)
        user = add_user(user)
        return jsonify(user.dict)

    def delete(self, user_id: int):

        user = get_user_by_id(user_id)
        request.session.delete(user)
        request.session.commit()
        return jsonify({"status": "deleted"})


user_view = UserView.as_view("user")
ads_view = AdsView.as_view("ads")

app.add_url_rule("/user/", view_func=user_view, methods=["POST"])

app.add_url_rule(
    "/user/<int:user_id>/", view_func=user_view, methods=["GET", "PATCH", "DELETE"]
)

app.add_url_rule("/ads/", view_func=ads_view, methods=["POST"])

app.add_url_rule(
    "/ads/<int:ad_id>/", view_func=ads_view, methods=["GET", "PATCH", "DELETE"]
)

app.run()
