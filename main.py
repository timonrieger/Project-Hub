from flask import Flask, render_template, url_for, flash, redirect, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from forms import AirNomadSocietyForm, NewsletterForm, ContactForm, FlashbackPlaylistsForm
import requests, os
from flask_bootstrap import Bootstrap5
from FlashbackPlaylists.spotify import PlaylistGenerator
from mail_manager import MailManager
from flask_wtf.csrf import CSRFProtect
from PIL import Image, ExifTags

FLASK_SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")
GMAIL_EMAIL = os.environ.get("GMAIL_EMAIL")
GMAIL_PASSWORD = os.environ.get("GMAIL_PASSWORD")
ANS_EMAIL = os.environ.get("ANS_EMAIL")
ANS_MAIL_PASSWORD = os.environ.get("ANS_MAIL_PASSWORD")
PRV_EMAIL = os.environ.get("PRV_EMAIL")

# website content storage using npoint
npoint_data = requests.get(url="https://api.npoint.io/498c13e5c27e87434a9f").json()

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY

csrf = CSRFProtect()
csrf.init_app(app)

bootstrap = Bootstrap5(app)

mail_manager = MailManager()

class Base(DeclarativeBase):
    __abstract__ = True

    confirmed: Mapped[int] = mapped_column(Integer, default=0)
    token: Mapped[str] = mapped_column(String, unique=True)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", "sqlite:///personal-website.db")
db = SQLAlchemy(app, model_class=Base)

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

class NewsletterSubs(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True)

with app.app_context():
    db.create_all()


@app.route("/", methods=["POST", "GET"])
def me():
    form = NewsletterForm()
    if form.validate_on_submit():
        already_subscriber = db.session.execute(db.Select(NewsletterSubs).where(NewsletterSubs.email == form.email.data)).scalar()
        if already_subscriber and already_subscriber.confirmed == 1:
            flash("You are already subscribed.", category="error")
        elif already_subscriber and already_subscriber.confirmed == 0:
            flash("Please check your inbox and click the confirmation link.", "error")
        else:
            newsletter_subscriber = NewsletterSubs(email=form.email.data, token=mail_manager.generate_token(expire=False))
            db.session.add(newsletter_subscriber)
            db.session.commit()
            sent = mail_manager.send_confirmation_email(form.email.data, GMAIL_EMAIL, GMAIL_PASSWORD, "newsletter", db, NewsletterSubs, AirNomads)
            if sent:
                flash(f"Confirmation email sent to {form.email.data}. Check your inbox and click the link.", category="success")
            if not sent:
                flash(f"Confirmation email could not be sent. To solve the issue send me an ", category="not_sent")

    return render_template("me.html", form=form, all_interests=npoint_data["interests"])

@app.route("/confirm")
def confirm_users():
    confirm_token = request.args.get("token")
    form = request.args.get("form")
    id = request.args.get("id")
    if form == "newsletter":
        member = db.session.execute(db.Select(NewsletterSubs).where(NewsletterSubs.id == id)).scalar()
        if member and member.confirmed == 1:
            flash("You have already confirmed your subscription. Stay tuned!", category="error")
        elif mail_manager.check_expiring_token(confirm_token, 600):
            member.confirmed = 1
            flash("Successfully subscribed.", category="success")
        else:
            db.session.delete(member)
            flash("Invalid confirmation token. Please fill in the form again.", category="error")
        db.session.commit()
        return redirect(url_for("me"))

    elif form == "ans":
        member = db.session.execute(db.Select(AirNomads).where(AirNomads.id == id)).scalar()
        if member and member.confirmed == 1:
            flash("You have already confirmed your subscription. Sit back and relax!", category="error")
            return redirect(url_for("ans_subscribe", id=id))
        elif mail_manager.check_expiring_token(confirm_token, 600):
            member.confirmed = 1
            db.session.commit()
            flash("Success! You are now an Air Nomad ✈️.", category="success")
            return redirect(url_for("ans_subscribe", id=id))
        else:
            return redirect(url_for("ans_subscribe", id=id, unsubscribe=True))


@app.route("/unsubscribe")
def unsubscribe_users():
    token = request.args.get("token")
    form = request.args.get("form")
    if form == "newsletter":
        member = db.session.execute(db.Select(NewsletterSubs).where(NewsletterSubs.token == token)).scalar()
        db.session.delete(member)
        db.session.commit()
        flash(f"Successfully unsubscribed with {member.email}.", category="success")
        return redirect(url_for("me"))

    elif form == "ans":
        member = db.session.execute(db.Select(AirNomads).where(AirNomads.token == token)).scalar()
        if member:
            return redirect(url_for("ans_subscribe", token=token, unsubscribe=True))
        if not member:
            flash("You are already unsubscribed.", category="error")
            return redirect(url_for("ans_subscribe"))

@app.route("/projects/air-nomad-society")
def air_nomad_society():
    return render_template("AirNomad.html")

@app.route("/projects/air-nomad-society/subscribe", methods=["POST", "GET"])
def ans_subscribe():
    token = request.args.get("token")
    id = request.args.get("id")
    unsubscribe = request.args.get("unsubscribe")
    form = AirNomadSocietyForm()

    if (token or id) and request.method == "GET":
        member = None
        if token:
            member = db.session.query(AirNomads).filter_by(token=token).scalar()
        elif id:
            member = db.session.query(AirNomads).filter_by(id=id).scalar()


        if not member:
            flash("No member found. Please subscribe to become a member.", category="error")
            return render_template("ans_subscribe.html", form=form, show_form=True)

        elif member and unsubscribe:
            form = AirNomadSocietyForm(
                username=member.username,
                email=member.email,
                departure_city=f"{member.departure_city} | {member.departure_iata}",
                currency=member.currency,
                min_nights=member.min_nights,
                max_nights=member.max_nights,
                favorite_countries=[country.strip() for country in member.travel_countries.split(",")]
            )
            if token: #user clicked unsubscribe link in email
                flash(f"You have successfully unsubscribed with {member.email}.", category="success")
                flash("Unsubscribed by mistake? To resubscribe, simply submit the form again.")
            elif id: #user clicked confirmation link too late
                flash("Invalid confirmation token. Please resubmit the form and click the link in the email within 10 minutes.", category="error")
            db.session.delete(member)
            db.session.commit()

            return render_template("ans_subscribe.html", form=form, show_form=True)


        elif member and token and not unsubscribe: #user clicked update link in email
            form = AirNomadSocietyForm(
                username=member.username,
                email=member.email,
                departure_city=f"{member.departure_city} | {member.departure_iata}",
                currency=member.currency,
                min_nights=member.min_nights,
                max_nights=member.max_nights,
                favorite_countries=[country.strip() for country in member.travel_countries.split(",")]
            )
            flash("Your profile is ready for updates. Please make any changes as needed.", category="success")
            return render_template("ans_subscribe.html", form=form, show_form=True, update=True)

        else:
            return render_template("ans_subscribe.html", form=form)

    if form.validate_on_submit() and request.method == 'POST':
        already_member = db.session.execute(db.Select(AirNomads).where(AirNomads.email == form.email.data)).scalar()
        favorite_countries = ",".join([country for country in form.favorite_countries.data])
        if already_member:
            if already_member.confirmed == 0:
                flash("Please check your inbox for an email from Air Nomad Society and click the link provided before proceeding.", "error")
            else:
                already_member.username = form.username.data
                already_member.departure_city = form.departure_city.data.split(" | ")[0]
                already_member.departure_iata = form.departure_city.data.split(" | ")[1]
                already_member.currency = form.currency.data
                already_member.min_nights = form.min_nights.data
                already_member.max_nights = form.max_nights.data
                already_member.travel_countries = favorite_countries
                db.session.commit()
                flash("Your preferences were changed successfully.", category="success")
                return render_template("ans_subscribe.html", form=form, update=True)
        if not already_member:
            new_member = AirNomads(
                username=form.username.data,
                email=form.email.data,
                departure_city=form.departure_city.data.split(" | ")[0],
                departure_iata=form.departure_city.data.split(" | ")[1],
                currency=form.currency.data,
                min_nights=form.min_nights.data,
                max_nights=form.max_nights.data,
                travel_countries=favorite_countries,
                token=mail_manager.generate_token(expire=False)
            )
            db.session.add(new_member)
            db.session.commit()
            sent = mail_manager.send_confirmation_email(form.email.data, ANS_EMAIL, ANS_MAIL_PASSWORD, "ans", db, NewsletterSubs, AirNomads, username=form.username.data)
            if sent:
                flash(f"Confirmation email sent to {form.email.data}. Check your inbox and click the link.",
                      category="success")
            if not sent:
                flash(f"Confirmation email could not be sent. To solve the issue send me an ", category="not_sent")

        return render_template("ans_subscribe.html", form=form)

    return render_template("ans_subscribe.html", form=form, show_form=True)


@app.route("/projects/air-nomad-society/example-email")
def ans_example_email():
    return render_template("ans_example_email.html")

@app.route("/projects/flashback-playlists", methods=["POST", "GET"])
def flashback_playlists():
    form = FlashbackPlaylistsForm()
    if form.validate_on_submit():
        date_input = str(form.date_input.data)
        year = int(date_input.split("-")[0])
        month = date_input.split("-")[1]
        day = date_input.split("-")[2]
        if year >= 1900:
            playlist_date = f"{year}-{month}-{day}"
            description = f"{form.description.data}\nCreated by https://www.timonrieger.com{request.endpoint}"
            playlist_link = PlaylistGenerator.generate_playlist(date=playlist_date, title=form.title.data, description=description)
            return render_template("FlashbackPlaylists.html", form_submitted=True, link=playlist_link, title=form.title.data, form=form)
        else:
            flash("Please enter a date that is later than 1900.", category="error")
            form = FlashbackPlaylistsForm(
                title=form.title.data,
                description=form.description.data
            )
            return render_template("FlashbackPlaylists.html", form=form)
    return render_template("FlashbackPlaylists.html", form=form)


@app.route("/projects")
def browse_projects():
    return render_template("projects.html", all_projects=npoint_data["projects"])

def get_exif_data(image_path):
    image = Image.open(image_path)
    exif_data = image._getexif()
    if exif_data is not None:
        exif = {
            ExifTags.TAGS.get(tag): value
            for tag, value in exif_data.items()
            if tag in ExifTags.TAGS
        }
        return exif
    else:
        return None

def get_exposure_info(exif):
    aperture = exif.get("FNumber")
    shutter_speed = exif.get("ExposureTime")
    iso = exif.get("ISOSpeedRatings")
    if aperture and shutter_speed and iso:
        aperture_value = aperture.numerator / aperture.denominator
        shutter_speed_value = round((shutter_speed.numerator / shutter_speed.denominator), 4)
        exposure_info = f"(f{aperture_value} | {shutter_speed_value}s | ISO {iso})"
        return exposure_info
    return None

def get_camera_full_name(exif):
    make = exif.get("Make", "").strip()
    model = exif.get("Model", "").strip()
    if make and model:
        return f"{make} {model}"
    elif model:
        return model
    else:
        return "Unknown Camera"

@app.route("/projects/photography")
def photography():
    photos_dir = 'static/images/photography'
    all_photos = []

    for filename in os.listdir(photos_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(photos_dir, filename)
            exif = get_exif_data(image_path)
            exposure_info = get_exposure_info(exif) if exif else ""
            camera_full_name = get_camera_full_name(exif) if exif else "Unknown Camera"
            photo_info = {
                "filename": filename,
                "camera": camera_full_name,
                "exposure": exposure_info
            }
            all_photos.append(photo_info)

    return render_template("Photography.html", all_photos=all_photos)

@app.route("/contact", methods=["POST", "GET"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        message = (f"Subject: Message by {form.name.data} from your Website\n\n"
                   f"Hello Timon,\n\n"
                   f"My name is {form.name.data}. You can contact me at {form.email.data}\n\n"
                   f"{form.message.data}\n\n")
        sent = mail_manager.send_basic_emails(GMAIL_EMAIL, GMAIL_PASSWORD, GMAIL_EMAIL, message)
        if sent:
            flash("Message successfully sent.", "success")
        elif not sent:
            flash("Message could not be sent. Try again later or send me an ", "not_sent")

    #return render_template("contact.html", form=form)
    return redirect(f'mailto:{PRV_EMAIL}')

@app.route('/robots.txt')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])

@app.errorhandler(404)
# inbuilt function which takes error as parameter
def not_found(e):
    # defining function
    return render_template("404.html"), 404

@app.after_request
def add_header(response):
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    return response


if __name__ == "__main__":
    app.run(debug=False)
