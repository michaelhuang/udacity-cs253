from google.appengine.ext import db

from lib import auth_helpers


class User(db.Model):
    name = db.StringProperty(required=True)
    pw_hash = db.StringProperty(required=True)
    email = db.StringProperty()

    @staticmethod
    def users_key(group='default'):
        return db.Key.from_path('users', group)

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent=cls.users_key())

    @classmethod
    def by_name(cls, name):
        u = User.all().filter('name =', name).get()
        return u

    @classmethod
    def register(cls, name, pw, email=None):
        pw_hash = auth_helpers.make_pw_hash(name, pw)
        return User(parent=cls.users_key(),
                    name=name,
                    pw_hash=pw_hash,
                    email=email)

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and auth_helpers.valid_pw(name, pw, u.pw_hash):
            return u


class Page(db.Model):
    content = db.TextProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)

    @staticmethod
    def parent_key(path):
        return db.Key().from_path('/root' + path, 'pages')

    @classmethod
    def by_path(cls, path):
        q = cls.all()
        q.ancestor(cls.parent_key(path))
        q.order('-created')
        return q

    @classmethod
    def by_id(cls, page_id, path):
        return cls.get_by_id(page_id, cls.parent_key(path))
