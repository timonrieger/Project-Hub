from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Email, Length, NumberRange
from wtforms import StringField, SelectField, IntegerField, SelectMultipleField, SubmitField, TextAreaField, DateField
from secret_keys import TRAVEL_DATA
import requests

STRING_FIELD_STYLE = "width: 40%; height: 30px; margin: auto; display: block"
TEXT_AREA_STYLE = "width: 40%; height: 100px; margin: auto; display: block"
SELECT_MULTIPLE_STYLE = "width: 40%; height: 150px; margin: auto; display: block"
SUBMIT_STYLE = "margin-bottom: 10px"

class AirNomadSocietySubscribe(FlaskForm):
    departure_choices = [f"{city["city"]} | {city["code"]}" for city in requests.get(url=TRAVEL_DATA).json()["cities"]]
    currency_choices = requests.get(url=TRAVEL_DATA).json()["currencies"]
    country_choices = [country["country"] for country in requests.get(url=TRAVEL_DATA).json()["countries"]]

    username = StringField(label="Username", validators=[DataRequired(), Length(min=3, max=10, message="Set a username within 3 - 8 characters.")], render_kw={"style": f"{STRING_FIELD_STYLE}"})
    email = StringField(label="Email", validators=[DataRequired(), Email()], render_kw={"style": f"{STRING_FIELD_STYLE}"})
    departure_city = SelectField(label="Departure City", choices=departure_choices, validators=[DataRequired()], render_kw={"style": f"{STRING_FIELD_STYLE}"})
    currency = SelectField(label="Currency", choices=currency_choices, validators=[DataRequired()], render_kw={"style": f"{STRING_FIELD_STYLE}"})
    min_nights = IntegerField(label="Minimum Nights", validators=[DataRequired(), NumberRange(min=1, message="Set to 1 or above.")], render_kw={"style": f"{STRING_FIELD_STYLE}"})
    max_nights = IntegerField(label="Maximum Nights", validators=[DataRequired(), NumberRange(max=365, message="Set to 365 or lower.")], render_kw={"style": f"{STRING_FIELD_STYLE}"})
    favorite_countries = SelectMultipleField(label="Favorite destinations", choices=country_choices, validators=[DataRequired()], render_kw={"style": f"{SELECT_MULTIPLE_STYLE}; f{SUBMIT_STYLE}"})
    join = SubmitField(label="Join Air Nomad Society")
    update = SubmitField(label="Update Preferences", render_kw={"style": "margin: 10px"})

class ContactForm(FlaskForm):
    name = StringField(label="Name", render_kw={"style": f"{STRING_FIELD_STYLE}"}, validators=[DataRequired()])
    email = StringField(label="Email", render_kw={"style": f"{STRING_FIELD_STYLE}"}, validators=[DataRequired(), Email()])
    message = TextAreaField(label="Message", render_kw={"style": f"{STRING_FIELD_STYLE}; height: 150px; f{SUBMIT_STYLE}"}, validators=[DataRequired()])
    submit = SubmitField(label="Send")

class NewsletterForm(FlaskForm):
    email = StringField(label="Email", render_kw={"style": f"{STRING_FIELD_STYLE}; f{SUBMIT_STYLE}"}, validators=[DataRequired(), Email()])
    submit = SubmitField(label="Stay updated")

class FlashbackPlaylists(FlaskForm):
    date_input = DateField(label="Date", render_kw={"style": f"{STRING_FIELD_STYLE}"}, validators=[DataRequired()])
    title = StringField(label="Playlist Title", render_kw={"style": f"{STRING_FIELD_STYLE}"}, validators=[DataRequired()])
    description = TextAreaField(label="Playlist Description", render_kw={"style": f"{TEXT_AREA_STYLE}; {SUBMIT_STYLE}"}, validators=[DataRequired(), Length(max=300, message="Maximum 300 characters.")])
    submit = SubmitField(label="Generate Playlist", render_kw={"onclick": "loading()"})