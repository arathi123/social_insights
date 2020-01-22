from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from .utils import configure_db_session

from .models import (
    DBSession,
    Base,
)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine, session = configure_db_session(settings)
    authnpolicy = AuthTktAuthenticationPolicy('seekrit', hashalg='sha512')
    authzpolicy = ACLAuthorizationPolicy()
    # TODO define ACL root later if required
    config = Configurator(settings=settings, authentication_policy=authnpolicy, authorization_policy=authzpolicy)
    config.include('pyramid_jinja2')
    config.include("cornice")
    config.add_static_view('static', 'static', cache_max_age=0)
    config.add_route('home_page', '/')
    config.add_route('smaccounts', '/{subsection}/{id}/{name}', path_info=r"/(?:smaccounts|follow)/.*")
    config.add_route('fb_login', '/login/fb')
    config.add_route('logout', '/logout')
    config.scan()
    return config.make_wsgi_app()
