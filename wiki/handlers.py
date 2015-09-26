import os
import webapp2
import jinja2
import logging

from lib import auth_helpers
from lib import valid_helpers
from lib import utils

from models import User
from models import Page

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


DEBUG = bool(os.environ['SERVER_SOFTWARE'].startswith('Development'))
if DEBUG:
    logging.getLogger().setLevel(logging.DEBUG)


# base handler
class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        params['gray_style'] = utils.gray_style
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = auth_helpers.make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and auth_helpers.check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))

    def not_found(self):
        self.error(404)
        self.write('<h1>404: not found</h1>')


# user stuff
class Signup(Handler):
    def get(self):
        next_url = self.request.headers.get('referer', '/')
        self.render("signup-form.html", next_url=next_url)

    def post(self):
        have_error = False

        next_url = str(self.request.headers.get('next_url'))
        if not next_url or next_url.startswith('/login'):
            next_url = '/'

        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')
        self.next_url = next_url

        params = dict(username=self.username,
                      email=self.email)

        if not valid_helpers.valid_username(self.username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not valid_helpers.valid_password(self.password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif not valid_helpers.valid_verify(self.password, self.verify):
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not valid_helpers.valid_email(self.email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        if have_error:
            self.render('signup-form.html', **params)
        else:
            self.done()

    def done(self):
        u = User.by_name(self.username)
        if u:
            msg = 'That user already exists.'
            self.render('signup-form.html', error_username=msg)
        else:
            u = User.register(self.username, self.password, self.email)
            u.put()
            self.login(u)
            self.redirect(self.next_url)


class Login(Handler):
    def get(self):
        next_url = self.request.headers.get('referer', '/')
        self.render('login-form.html', next_url=next_url)

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        next_url = str(self.request.headers.get('next_url'))
        if not next_url or next_url.startswith('/login'):
            next_url = '/'

        u = User.login(username, password)
        if u:
            self.login(u)
            self.redirect(next_url)
        else:
            msg = 'Invalid login'
            self.render('login-form.html', error=msg)


class Logout(Handler):
    def get(self):
        next_url = self.request.headers.get('referer', '/')
        self.logout()
        self.redirect(next_url)


# wiki stuff
class NoSlash(Handler):
    def get(self, path):
        new_path = path.rstrip('/') or '/'
        self.redirect(new_path)


class EditPage(Handler):
    def get(self, path):
        if not self.user:
            self.redirect('/login')

        v = self.request.get('v')
        p = None
        if v:
            if v.isdigit():
                p = Page.by_id(int(v), path)
            if not p:
                return self.not_found()
        else:
            p = Page.by_path(path).get()
        self.render('edit.html', path=path, page=p)

    def post(self, path):
        if not self.user:
            self.error(400)
            return

        content = self.request.get('content')
        old_page = Page.by_path(path).get()
        if not (old_page or content):
            return
        elif not old_page or old_page.content != content:
            p = Page(parent=Page.parent_key(path), content=content)
            p.put()

        self.redirect(path)


class HistoryPage(Handler):
    def get(self, path):
        q = Page.by_path(path)
        q.fetch(100)

        posts = list(q)
        if posts:
            self.render('history.html', path=path, posts=posts)
        else:
            self.redirect('/_edit' + path)


class WikiPage(Handler):
    def get(self, path):
        v = self.request.get('v')
        p = None
        if v:
            if v.isdigit():
                p = Page.by_id(int(v), path)
            if not p:
                return self.not_found()
        else:
            p = Page.by_path(path).get()
        if p:
            self.render('page.html', path=path, page=p)
        else:
            self.redirect('/_edit' + path)
