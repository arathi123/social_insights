from sqlalchemy import (
    Column,
    BigInteger,
    String,
    ForeignKey,
    DateTime,
    Integer,
    Text,
    Boolean,
    Float,
    func
)

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import relationship
import json
# from urllib.parse import urlparse

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
)
from sqlalchemy.sql.schema import UniqueConstraint, Index

from zope.sqlalchemy import ZopeTransactionExtension
from datetime import datetime

DBSession = scoped_session(sessionmaker(
    extension=ZopeTransactionExtension(), expire_on_commit=False, autoflush=True))
Base = automap_base()


class User(Base):
    __tablename__ = 'users'

    user_id = Column(BigInteger, primary_key=True)
    user_email = Column(String(250))
    fb_user_name = Column(String(250))
    access_token = Column(String(300))

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def get_json(self):
        return json.dumps(self.as_dict())

    @staticmethod
    def register_user(user_id, fb_user_name, access_token, user_email):
        user = DBSession.query(User).filter(
            User.user_id == int(user_id)).first()
        # register user if not already registered
        if not user:
            user = User(user_id=int(user_id), fb_user_name=fb_user_name,
                        access_token=access_token, user_email=user_email)
            DBSession.add(user)

        return user

    @staticmethod
    def _get_auth_tkt(user):
        authenticated_user = DBSession.query(AuthenticatedUser).filter(
            AuthenticatedUser.user_id == int(user.user_id)).first()
        # register user if not already registered
        if authenticated_user:
            auth_tkt = authenticated_user.auth_tkt
        else:
            random_string = str(
                int((datetime.now() - datetime.utcfromtimestamp(0)).total_seconds()))
            auth_tkt = str(user.user_id) + random_string
            user = AuthenticatedUser(auth_tkt=auth_tkt, user_id=int(
                user.user_id), last_active_time=datetime.utcnow())
            DBSession.add(user)
        # TODO: encrypt the id with a random salt to prevent misuse of id
        return auth_tkt

    @staticmethod
    def get_user_from_auth_tkt(auth_tkt):
        authenticated_user = DBSession.query(AuthenticatedUser).filter(
            AuthenticatedUser.auth_tkt == auth_tkt).first()
        if authenticated_user:
            authenticated_user.last_active_time = datetime.utcnow()
            return authenticated_user.user
        else:
            return None

    @staticmethod
    def expire_auth_tkt(auth_tkt):
        authenticated_user = DBSession.query(AuthenticatedUser).filter(
            AuthenticatedUser.auth_tkt == auth_tkt).first()
        if authenticated_user:
            DBSession.delete(authenticated_user)


class AuthenticatedUser(Base):
    __tablename__ = 'authenticated_users'

    auth_tkt = Column(String(200), primary_key=True)
    user_id = Column(ForeignKey('users.user_id'))
    last_active_time = Column(DateTime)

    user = relationship('User')


class SmAccounts(Base):
    __tablename__ = 'sm_accounts'
    sm_account_id = Column(BigInteger, primary_key=True)
    sm_domain = Column(String(250))
    sm_url = Column(String(250))


class UsersSmAccount(Base):
    __tablename__ = 'users_sm_accounts'

    user_id = Column(ForeignKey('users.user_id'), nullable=False)
    sm_account_id = Column(ForeignKey(
        'sm_accounts.sm_account_id'), nullable=False)
    user_sm_account_id = Column(Integer, primary_key=True)

    sm_account = relationship('SmAccounts')
    user = relationship('User')


class Interactions(Base):
    __tablename__ = 'interactions'
    id = Column(String(300), primary_key=True, autoincrement=False)
    message = Column(Text)
    is_page_post = Column(Boolean)
    like_count = Column(Integer)
    parent_id = Column(String(300))
    author_id = Column(BigInteger)
    author_name = Column(String(200))
    sm_account_id = Column(BigInteger, ForeignKey('sm_accounts.sm_account_id'))
    created_date = Column(DateTime)
    updated_date = Column(DateTime)
    scraped_date = Column(DateTime)
    sm_account = relationship('SmAccounts')

    @staticmethod
    def get_value_from_json(key, interaction_raw):
        try:
            return interaction_raw[key]
        except KeyError as e:
            # TODO: Add logging to print missing key
            return None

    @classmethod
    def get_date_from_key(cls, key, interaction_raw):
        str_date = cls.get_value_from_json(key, interaction_raw)
        if str_date is not None:
            date_val = datetime.strptime(str_date, '%Y-%m-%dT%H:%M:%S%z')
            return date_val
        else:
            return None

    @classmethod
    def get_sender_id(cls, interaction_raw):
        sender = cls.get_value_from_json('from', interaction_raw)
        return sender.get('id', None)

    @classmethod
    def get_author_info(cls, interaction_raw):
        sender = cls.get_value_from_json('from', interaction_raw)
        author_id = sender.get('id', None)
        author_name = sender.get('name', None)
        return author_id, author_name

    @classmethod
    def get_num_likes(cls, interaction_raw):
        if 'likes' in interaction_raw:
            return interaction_raw['likes']['summary']['total_count']
        elif 'like_count' in interaction_raw:
            return interaction_raw['like_count']
        else:
            return 0

    @classmethod
    def get_interaction_from_json(cls, sm_account_id, interaction_raw, parent_id=None):
        interaction_id = cls.get_value_from_json('id', interaction_raw)
        message = cls.get_value_from_json('message', interaction_raw)
        created_date = cls.get_date_from_key('created_time', interaction_raw)
        updated_date = cls.get_date_from_key('updated_time', interaction_raw)
        if updated_date is None:
            updated_date = created_date
        scraped_date = datetime.utcnow()
        sender_id = cls.get_sender_id(interaction_raw)
        is_page_post = True if str(sm_account_id) == sender_id else False
        author_id, author_name = cls.get_author_info(interaction_raw)
        num_likes = cls.get_num_likes(interaction_raw)
        return cls(sm_account_id=sm_account_id, id=interaction_id, message=message, created_date=created_date,
                   updated_date=updated_date,
                   scraped_date=scraped_date, is_page_post=is_page_post, like_count=num_likes, parent_id=parent_id,
                   author_id=author_id, author_name=author_name)

    @classmethod
    def get_nested_interactions(cls, sm_account_id, interaction_raw, interactions_set, batch_requests=[],
                                parent_id=None):
        interaction = cls.get_interaction_from_json(sm_account_id, interaction_raw, parent_id)
        interactions_set.add(interaction)
        if 'comments' in interaction_raw:
            comments_data = interaction_raw['comments']
            cls.get_interactions_from_comments(sm_account_id, comments_data, interactions_set, batch_requests,
                                               interaction.id)

        return interactions_set, batch_requests

    @classmethod
    def get_interactions_from_comments(cls, sm_account_id, comments_data, interactions_set, batch_requests, parent_id):
        if 'data' in comments_data:
            comments = comments_data['data']
            for comment in comments:
                cls.get_nested_interactions(sm_account_id, comment, interactions_set, batch_requests, parent_id)
        # if 'paging' in comments_data and 'next' in comments_data['paging']:
        #     next_url = urlparse(comments_data['paging']['next'])
        #     relative_url = next_url.path + '?' + next_url.query + '&include_headers=false'
        #     req = {'method': 'GET', 'relative_url': relative_url, 'parent_id': parent_id}
        #     batch_requests.append(req)

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        ids = self.id.split('_')
        return sum([int(id) for id in ids]) % 10111


class CategoryGroup(Base):
    __tablename__ = 'category_group'
    category_group_id = Column(Integer, primary_key=True)
    name = Column(String(30))


class Category(Base):
    __tablename__ = 'category'
    category_id = Column(Integer, primary_key=True)
    name = Column(String(30))
    category_group_id = Column(ForeignKey('category_group.category_group_id'))

    category_group = relationship('CategoryGroup')


class InteractionCategory(Base):
    __tablename__ = 'interaction_category'

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('users.user_id'), nullable=False)
    interaction_id = Column(ForeignKey('interactions.id'), nullable=False)
    category_id = Column(ForeignKey('category.category_id'), nullable=False)
    sm_account_id = Column(ForeignKey('sm_accounts.sm_account_id'), nullable=False)
    created_date = Column(DateTime)

    user = relationship('User')
    interaction = relationship('Interactions')
    category = relationship('Category')
    sm_account = relationship('SmAccounts')

    __table_args__ = (UniqueConstraint('user_id', 'interaction_id', 'category_id', name='int_cat_u_idx'),
                      Index('int_sm_cat_idx', id.desc(), sm_account_id, category_id,
                            postgresql_where=user_id == 1))


class ModelTrainingLog(Base):
    __tablename__ = 'model_training_logs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    category_group_id = Column(ForeignKey('category_group.category_group_id'))
    validation_type = Column(String)
    avg_precision = Column(Float)
    avg_recall = Column(Float)
    avg_fscore = Column(Float)
    avg_accuracy = Column(Float)
    avg_test_support = Column(Integer)
    avg_train_support = Column(Integer)
    serialized_model = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    support = Column(Integer)
    category_group = relationship('CategoryGroup')


class ModelApplicationLog(Base):
    __tablename__ = 'model_application_logs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    model_id = Column(ForeignKey('model_training_logs.id'))
    category_group_id = Column(ForeignKey('category_group.category_group_id'))
    sm_account_id = Column(ForeignKey('sm_accounts.sm_account_id'), nullable=False)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    processed_interactions = Column(Integer)

    category_group = relationship('CategoryGroup')
    sm_account = relationship('SmAccounts')
    training_log = relationship('ModelTrainingLog')
