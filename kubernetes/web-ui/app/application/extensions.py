from flask_wtf import CSRFProtect

csrf = CSRFProtect()
csrf._exempt_views.add('dash.dash.dispatch')
