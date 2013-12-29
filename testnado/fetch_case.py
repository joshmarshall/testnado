class FetchCase(object):

    def fetch(self, *args, **kwargs):

        # it's really annoying when Tornado automatically follows redirects.
        # I set this to be false by default, because explicit > implicit.
        # Override by specifying follow_redirects=True

        kwargs.setdefault("follow_redirects", False)
        return super(FetchCase, self).fetch(*args, **kwargs)
