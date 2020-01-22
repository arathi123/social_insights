import json
from datetime import datetime

import transaction
from .categorization_model import CategorizationModel
from cornice import Service
from social_insights.models import CategoryGroup
from sqlalchemy import func, desc
from webob import Response, exc

from .datacollection.fb_posts_collector import collect_fb_posts
from .models import Base, DBSession, User, SmAccounts, UsersSmAccount, Interactions, Category, InteractionCategory

info_desc = "This service provides rest API interface for sosilee"
sosilee_service = Service(name='sosilee', path='/api', description=info_desc)
feed_service = Service(name='feed', path='/feed', description="Feed service rest API")
sm_accounts_service = Service(name='sm_accounts', path='/sm_accounts')
user_service = Service(name='users', path='/user',
                       description="User management rest API")
category_service = Service(name='categorize', path='/category',
                           description="Categorize interaction rest API")
FEED_PAGE_SIZE = 20

general_category_group = DBSession.query(CategoryGroup).filter(CategoryGroup.name == 'General').first()
engine = Base.metadata.bind


@sosilee_service.get()
def get_status(request):
    return {'status': 'success'}


def validate_user(request):
    user = User.get_user_from_auth_tkt(request.authenticated_userid)
    if user is None:
        raise _401()
    else:
        request.validated['user'] = user


class _401(exc.HTTPError):
    def __init__(self, msg='Unauthorized'):
        body = {'status': 401, 'message': msg}
        Response.__init__(self, json.dumps(body))
        self.status = 401
        self.content_type = 'application/json'


@feed_service.get(validators=validate_user)
def get_feed(request):
    # get the feeds from facebook page the user has signed up
    paging_id = request.GET.get('pagingID')
    sm_account_id = request.GET.get('sm_account_id')
    user = request.validated["user"]
    interactions = {'data': []}

    sm_accounts = [acc.sm_account_id for acc in _get_user_sm_accounts(user)]

    complaint_id = DBSession.query(Category.category_id).filter(Category.name == 'Complaint').scalar()
    interaction_ids = DBSession.query(InteractionCategory.interaction_id, InteractionCategory.id).filter(
        InteractionCategory.user_id == 1).filter(InteractionCategory.category_id == complaint_id).filter(
        InteractionCategory.sm_account_id.in_(sm_accounts))

    if sm_account_id:
        interaction_ids = interaction_ids.filter(InteractionCategory.sm_account_id == sm_account_id)

    if not paging_id:
        paging_id_query = DBSession.query(func.max(InteractionCategory.id))
        paging_id = paging_id_query.one_or_none()

    if paging_id:
        interaction_ids = interaction_ids.filter(InteractionCategory.id < paging_id)

    interaction_ids = interaction_ids.order_by(desc(InteractionCategory.id)).limit(FEED_PAGE_SIZE)

    ic_view = interaction_ids.subquery().alias("interaction_ids")
    feed = DBSession.query(Interactions, ic_view.c.id).join(ic_view)

    int_cat_id = None
    for interaction, int_cat_id in feed:
        if interaction.author_name is None:
            interactions['data'].append(
                {'created_time': interaction.created_date.strftime("%Y-%m-%dT%H:%M:%S +0000"),
                 'from': {'name': 'Anonymous User', 'id': 'Not Available'}, 'message': interaction.message,
                 'id': interaction.id, 'account_name': interaction.sm_account.sm_domain})
        else:
            interactions['data'].append(
                {'created_time': interaction.created_date.strftime("%Y-%m-%dT%H:%M:%S +0000"),
                 'from': {'name': interaction.author_name, 'id': interaction.author_id},
                 'message': interaction.message, 'id': interaction.id,
                 'account_name': interaction.sm_account.sm_domain})
    if int_cat_id:
        interactions['paging_id'] = int_cat_id

    return interactions


@sm_accounts_service.get(validators=validate_user)
def get_sm_accounts(request):
    user = request.validated["user"]
    user_sm_accounts = _get_user_sm_accounts(user)
    sm_accounts = {'sm_accounts': []}
    for user_sm_account in user_sm_accounts:
        sm_account = user_sm_account.sm_account
        sm_accounts['sm_accounts'].append(
            {'name': sm_account.sm_domain, 'url': sm_account.sm_url, 'id': sm_account.sm_account_id})
    return sm_accounts


def _get_user_sm_accounts(user):
    user_sm_accounts = DBSession.query(UsersSmAccount).filter(UsersSmAccount.user_id == user.user_id).all()
    return user_sm_accounts


@sm_accounts_service.post(validators=validate_user)
def follow_sm_account(request):
    user = request.validated["user"]
    sm_account_id = request.POST.get('sm_account_id')
    sm_domain = request.POST.get('sm_domain')
    sm_url = "https://www.facebook.com/{}".format(sm_account_id)
    action = request.POST.get('action')
    if action == 'follow':
        sm_account = DBSession.query(SmAccounts).filter(
            SmAccounts.sm_account_id == int(sm_account_id)).first()
        if sm_account is None:
            sm_account = SmAccounts(
                sm_account_id=sm_account_id, sm_domain=sm_domain, sm_url=sm_url)
            user_sm_account = UsersSmAccount(user=user, sm_account=sm_account)
            with transaction.manager:
                DBSession.add(user_sm_account)
            collect_fb_posts(sm_account_id=sm_account.sm_account_id, access_token=user.access_token, session=DBSession,
                             days=5, limit=100, cutoff=500)
            CategorizationModel.apply(general_category_group, engine, DBSession, sm_account_id)
        else:
            user_sm_account = DBSession.query(UsersSmAccount).filter(UsersSmAccount.user_id == user.user_id).filter(
                UsersSmAccount.sm_account_id == sm_account_id).first()
            if user_sm_account is None:
                user_sm_account = UsersSmAccount(user=user, sm_account=sm_account)
                DBSession.add(user_sm_account)
    elif action == 'unfollow':
        sm_account = DBSession.query(UsersSmAccount).filter(
            UsersSmAccount.sm_account_id == int(sm_account_id)).filter(UsersSmAccount.user_id == user.user_id).delete()
    return {'status': 'success'}


@category_service.get(validators=validate_user)
def get_category(request):
    category_group_id = request.get('category_group')
    categories = {'category': []}
    if category_group_id is None:
        for category in DBSession.query(Category):
            categories['category'].append(
                {'name': category.name, 'categoryId': category.category_id,
                 'categoryGroup': category.category_group_id})
    else:
        for category in DBSession.query(Category).filter(Category.category_group_id == category_group_id):
            categories['category'].append(
                {'name': category.name, 'categoryId': category.category_id,
                 'categoryGroup': category.category_group_id})
    return categories


@category_service.post(validators=validate_user)
def categroize_interaction(request):
    user = request.validated["user"]
    interaction_id = request.POST.get('interaction_id')
    category_id = request.POST.get('category_id')
    action = request.POST.get('action')
    created_date = datetime.now()
    if action == 'add':
        interaction_category = InteractionCategory(user_id=user.user_id, interaction_id=interaction_id,
                                                   category_id=category_id, created_date=created_date)
        DBSession.add(interaction_category)
    elif action == 'remove':
        interaction_category = DBSession.query(InteractionCategory).filter(
            InteractionCategory.interaction_id == int(interaction_id),
            InteractionCategory.user_id == user.user_id).delete()
    return {'status': 'success'}
