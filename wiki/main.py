import webapp2
import handlers

PAGE_RE = r'(/(?:[a-zA-Z0-9_-]+/?)*)'

app = webapp2.WSGIApplication([('/signup', handlers.Signup),
                               ('/login', handlers.Login),
                               ('/logout', handlers.Logout),
                               ('/_edit' + PAGE_RE, handlers.EditPage),
                               ('/_history' + PAGE_RE, handlers.HistoryPage),
                               (PAGE_RE, handlers.WikiPage),
                               ],
                              debug=True)
