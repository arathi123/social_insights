import os
import sys
import transaction
import csv

from pyramid.paster import (
    get_appsettings,
    setup_logging,
)

from pyramid.scripts.common import parse_vars
# TODO sample code to be modified later
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from ..utils import configure_db_session
from ..models import (
    InteractionCategory,
    User,
    CategoryGroup,
    Category,
    Interactions,
    SmAccounts)

from datetime import datetime
import pandas as pd
import logging


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)
    engine, session = configure_db_session(settings)

    data = pd.read_csv('interaction_category_sample.csv')
    airtel_sample = pd.read_csv('airtel_sample.csv', quotechar='`', sep=',', quoting=csv.QUOTE_ALL).fillna('')

    #   Seed data to category_group, category
    with transaction.manager:
        session.merge(User(user_id=1, user_email='system@sosilee.com', fb_user_name='system'))
        session.merge(User(user_id=400, user_email='testuser@sosilee.com', fb_user_name='test_user'))
        try:
            category_group_details = session.query(CategoryGroup).filter(CategoryGroup.name == 'General').one()
        except NoResultFound:
            category_group_details = CategoryGroup(name='General')
            session.merge(category_group_details)
            category_group_details = session.query(CategoryGroup).filter(CategoryGroup.name == 'General').first()
            session.merge(Category(name='Complaint', category_group=category_group_details))
            session.merge(Category(name='Others', category_group=category_group_details))
            session.merge(Category(name='New', category_group=category_group_details))
            session.merge(SmAccounts(sm_account_id=147351511955143, sm_domain='Airtel India',
                                     sm_url='https://www.facebook.com/147351511955143'))

        for index, rows in airtel_sample.iterrows():
            author_id = int(rows['author_id']) if rows['author_id'] else None
            try:
                data_exists = session.query(Interactions).filter(Interactions.id == str(rows['id'])).one()
                logging.info("Seed data already available, skipping insertion ..")
                break
            except NoResultFound as e:
                session.merge(Interactions(id=str(rows['id']), message=rows['message'],
                                           is_page_post=str(rows['is_page_post']), like_count=rows['like_count'],
                                           parent_id=rows['parent_id'], sm_account_id=rows['sm_account_id'],
                                           created_date=rows['created_date'], updated_date=rows['updated_date'],
                                           scraped_date=rows['scraped_date'], author_id=author_id,
                                           author_name=rows['author_name']))

    # Seed data to interaction_category
    try:
        with transaction.manager:
            user_details = session.query(User).filter(User.user_email == 'testuser@sosilee.com').first()
            for index, rows in data.iterrows():
                complaint = session.query(Category). \
                    filter((Category.name == str(rows['is_complaint'])) &
                           (Category.category_group_id == category_group_details.category_group_id)).first()
                record = InteractionCategory(user_id=user_details.user_id,
                                             interaction_id=str(rows['id']),
                                             category_id=complaint.category_id,
                                             sm_account_id=147351511955143,
                                             created_date=datetime.utcnow())
                session.merge(record)
    except IntegrityError:
        logging.info("Seed data already available.")
