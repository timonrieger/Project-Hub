from flask import Flask, render_template, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
from forms import AirNomadSocietySubscribe, NewsletterForm, ContactForm, FlashbackPlaylists
import requests
from flask_bootstrap import Bootstrap5
from FlashbackPlaylists.spotify import PlaylistGenerator
from secret_keys import FLASK_SECRET_KEY

# website content storage using npoint
data = requests.get(url="https://api.npoint.io/498c13e5c27e87434a9f").json()

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY
bootstrap = Bootstrap5(app)

class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///project_webpage.db"
db = SQLAlchemy(model_class=Base)
db.init_app(app)

class AirNomads(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String, unique=True)
    departure_city: Mapped[str] = mapped_column(String)
    departure_iata: Mapped[str] = mapped_column(String)
    currency: Mapped[str] = mapped_column(String)
    min_nights: Mapped[int] = mapped_column(Integer)
    max_nights: Mapped[int] = mapped_column(Integer)
    travel_countries: Mapped[str] = mapped_column(String)

class NewsletterSubscribers(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True)

with app.app_context():
    db.create_all()


@app.route("/", methods=["POST", "GET"])
def home():
    form = NewsletterForm()
    if form.validate_on_submit():
        already_subscriber = db.session.execute(db.Select(NewsletterSubscribers).where(NewsletterSubscribers.email == form.email.data)).scalar()
        if already_subscriber:
            flash("You have subscribed already.")
        if not already_subscriber:
            newsletter_subscriber = NewsletterSubscribers(email=form.email.data)
            db.session.add(newsletter_subscriber)
            db.session.commit()
            flash("Successfully subscribed.")
    return render_template("index.html", form=form)

@app.route("/projects")
def browse_projects():
    return render_template("projects.html", all_projects=data["projects"])

@app.route("/contact", methods=["POST", "GET"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        form.message(style="height: 200px")
        return render_template("contact.html", form=form, form_submitted=True)
    return render_template("contact.html", form=form)

@app.route("/air-nomad-society", methods=["POST", "GET"])
def air_nomad_society():
    form = AirNomadSocietySubscribe()
    if form.validate_on_submit():
        already_member = db.session.execute(db.Select(AirNomads).where(AirNomads.email == form.email.data)).scalar()
        favorite_countries = ",".join([country for country in form.favorite_countries.data])
        if already_member:
            if form.update.data:
                already_member.username = form.username.data
                already_member.departure_city = form.departure_city.data.split(" | ")[0]
                already_member.departure_iata = form.departure_city.data.split(" | ")[1]
                already_member.currency = form.currency.data
                already_member.min_nights = form.min_nights.data
                already_member.max_nights = form.max_nights.data
                already_member.travel_countries = favorite_countries
                db.session.commit()
                flash("Your preferences were changed successfully.")
            elif form.join.data:
                flash("You are already a member. Update instead.")
        if not already_member:
            if form.update.data:
                flash("You aren't a member yet. Join first.")
            elif form.join.data:
                new_member = AirNomads(
                    username=form.username.data,
                    email=form.email.data,
                    departure_city=form.departure_city.data.split(" | ")[0],
                    departure_iata=form.departure_city.data.split(" | ")[1],
                    currency=form.currency.data,
                    min_nights=form.min_nights.data,
                    max_nights=form.max_nights.data,
                    travel_countries=favorite_countries
                )
                db.session.add(new_member)
                db.session.commit()
                flash("Success. You are now an Air Nomad ✈️")

    return render_template("AirNomad.html", form=form)

@app.route("/flashback-playlists", methods=["POST", "GET"])
def flashback_playlists():
    form = FlashbackPlaylists()
    if form.validate_on_submit():
        date_input = str(form.date_input.data)
        year = int(date_input.split("-")[0])
        month = date_input.split("-")[1]
        day = date_input.split("-")[2]
        if year >= 1900:
            playlist_date = f"{year}-{month}-{day}"
            playlist_link = PlaylistGenerator.generate_playlist(date=playlist_date, title=form.title.data, description=form.description.data)
            return render_template("FlashbackPlaylists.html", form_submitted=True, link=playlist_link, title=form.title.data, form=form)
        else:
            flash("Please enter a date that is later than 1900.")
            form = FlashbackPlaylists(
                title=form.title.data,
                description=form.description.data
            )
            return render_template("FlashbackPlaylists.html", form=form)
    return render_template("FlashbackPlaylists.html", form=form)

if __name__ == "__main__":
    app.run(debug=True)