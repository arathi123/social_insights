from datetime import datetime

from authomatic.adapters import WebObAdapter
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember, forget
from pyramid.view import view_config

from social_insights.models import User
from .authomaic_config import authomatic

@view_config(route_name='home_page', renderer='templates/home_page.jinja2')
def home_page(request):
    user = User.get_user_from_auth_tkt(request.authenticated_userid)
    return {'user': user}

@view_config(route_name='smaccounts', renderer='templates/home_page.jinja2')
def smaccounts(request):
    user = User.get_user_from_auth_tkt(request.authenticated_userid)
    return {'user': user}


@view_config(route_name='fb_login')
def fb_login(request):
    """
    Login using Facebook and generate auth token

    :param request:
    :return:
    """

    response = HTTPFound(location=request.route_url('home_page'))
    provider_name = 'fb'
    result = authomatic.login(WebObAdapter(request, response), provider_name)
    # if result and result.user.credentials:
    #     # get fb authenticated user
    #     result.user.update()
    user=User.register_user(32341235034,"arti","dsfjdy3aodfi3adfj330dsfmadi3","mseca@gmail.com")
    # user = User.register_user(result.user.id,result.user.name,result.user.credentials.token,result.user.email)# Generate auth token
    auth_tkt = User._get_auth_tkt(user)
    header = remember(request, auth_tkt)
    # Add auth token headers to response
    header_list = response._headerlist__get()
    [header_list.append(auth_header) for auth_header in header]
    response._headerlist__set(header_list)
    return response


@view_config(route_name='logout')
def logout(request):
    """
    Logout user and invalidate auth token
    :param request:
    :return:
    """
    headers = forget(request)
    auth_tkt = request.authenticated_userid
    User.expire_auth_tkt(auth_tkt)
    return HTTPFound(headers=headers,location=request.route_url("home_page"))
