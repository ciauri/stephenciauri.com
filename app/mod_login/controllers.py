# Import flask dependencies
from flask import Blueprint, request, render_template, \
    flash, g, session, redirect, url_for
# Import password / encryption helper tools
from werkzeug.security import check_password_hash, generate_password_hash
# Import the database object from the main app module
from app import db
# Import module forms
from app.mod_login.forms import LoginForm
# Import module models (i.e. User)
from app.mod_login.models import User

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_login = Blueprint('login', __name__, url_prefix='/login')


# Set the route and accepted methods
@mod_login.route('/signin/', methods=['GET', 'POST'])
def signin():
    # If sign in form is submitted
    form = LoginForm(request.form)

    # Verify the sign in form
    if form.validate_on_submit():
        print("lolk")

        user = User.query.filter_by(email=form.email.data).first()

        if user and check_password_hash(user.password, form.password.data):
            print("success")
            session['user_id'] = user.id
            flash('Welcome %s' % user.name)
            users = User.query.all()

            return render_template("login/suckers.html", users=users)
        else:
            if user:
                flash('Wrong email or password', 'error')
            else:
                user = User(name="nubsauce", email=form.email.data, password=generate_password_hash(form.password.data))
                user.status = 0
                user.role = 0
                db.session.add(user)
                db.session.commit()

    return render_template("login/signin.html", form=form, header="LoLogin")
