# TODO sample code to be modified later
import logging
from datetime import datetime

import pandas as pd
import transaction
from sklearn.base import BaseEstimator
from sklearn.base import clone
from sklearn.model_selection import StratifiedKFold
from sklearn.externals import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics.classification import precision_recall_fscore_support, accuracy_score
from sklearn.pipeline import Pipeline
from social_insights.models import InteractionCategory, Interactions, Category, User, ModelApplicationLog
from sqlalchemy.sql import func, exists
from sqlalchemy.sql.expression import desc
from sqlalchemy.sql.operators import and_

from .models import ModelTrainingLog
import numpy as np
import os


class CategorizationModel(BaseEstimator):
    def __init__(self, category_group, engine, session, model_path=None, new_labelled_threshold=0, apply_model=False,
                 sm_account_id=None):
        self.logger = logging.getLogger(__name__)
        self.category_group = category_group
        self.category = category_group.name
        self.engine = engine
        self.session = session
        self.logger.info("model path: {}".format(model_path))
        self.logger.info("new labelled threshold: {}".format(new_labelled_threshold))
        if apply_model:
            self.sm_account_id = sm_account_id
            self.apply_model(sm_account_id)
        else:
            self.new_labelled_threshold = new_labelled_threshold
            self.model_path = model_path
            self.check_path(model_path, self.logger)
            self.prepare_model()

    @classmethod
    def apply(cls, category_group, engine, session, sm_account_id=None):
        return cls(category_group, engine, session, apply_model=True, sm_account_id=sm_account_id)

    @staticmethod
    def check_path(model_path, logger):
        if not os.access(model_path, os.W_OK):
            logger.exception("Write access denied in Model path {}".format(model_path))
            raise ValueError("Write access denied in Model path {}".format(model_path))
        if not os.path.isabs(model_path):
            raise ValueError("Model path {} not supported. Please use absolute path.".format(model_path))

    def prepare_model(self):
        self.logger.info("Preparing model training")
        new_labelled_count = self.count_new_labelled_data()
        should_retrain = new_labelled_count > self.new_labelled_threshold
        if should_retrain:
            self.training_log = ModelTrainingLog(category_group=self.category_group, start_time=datetime.now())
            with transaction.manager:
                self.session.add(self.training_log)
            self.prepare_data(self.engine)
            self.prepare_pipeline()
            self.evaluate_model()
            self.fit(self.X, self.y)
            self.save_model()

    def count_new_labelled_data(self):
        last_training_date = self.session.query(func.max(ModelTrainingLog.end_time)).filter(
            ModelTrainingLog.category_group == self.category_group).scalar()
        if not last_training_date:
            last_training_date = datetime(2016, 5, 1)
        self.logger.info('Last model training date: {}'.format(last_training_date))
        query = self.session.query(func.count(Interactions.id).label('sample_count')).join(
            InteractionCategory).join(Category).filter(and_(
            Category.category_group == self.category_group,
            InteractionCategory.created_date > last_training_date
        ))
        self.logger.info(query)
        new_labelled_sample_count = query.scalar()
        self.logger.info("{} new labelled samples available".format(new_labelled_sample_count))
        return new_labelled_sample_count

    def prepare_data(self, engine):

        querying_trainset = (''' SELECT e.*,
                                       c.category_id
                                FROM
                                  (SELECT interaction_id,
                                          category_id
                                   FROM
                                     (SELECT interaction_id,
                                             category_id,
                                             RANK() over (partition BY interaction_id,category_id
                                                          ORDER BY cnt DESC) AS category_id_rank
                                      FROM
                                        (SELECT interaction_id,
                                                category_id,
                                                COUNT(category_id) AS cnt
                                         FROM interaction_category
                                         WHERE user_id != 1
                                         GROUP BY interaction_id,
                                                  category_id)a)b
                                   WHERE b.category_id_rank =1)c
                                JOIN category d ON c.category_id = d.category_id
                                JOIN interactions e ON e.id = c.interaction_id
                                WHERE category_group_id = '%s'
                                  AND e.is_page_post = 'f'
                                  AND length(e.message) > 2 ''') % self.category_group.category_group_id

        train_df = pd.read_sql(querying_trainset, engine)
        self.X = train_df.message
        self.y = train_df.category_id
        self.logger.info("Training data: {}, Labels: {}".format(self.X.shape, self.y.shape))

    def prepare_pipeline(self):
        self.clf = LogisticRegression()
        self.pipeline = Pipeline([
            ('vect', CountVectorizer(binary=True)),
            ('clf', self.clf),
        ])

    def evaluate_model(self):
        cv = StratifiedKFold(self.y, 3, shuffle=True, random_state=11)
        cv_metrics = self.get_cv_metrics(cv)
        t_log = self.training_log
        t_log.validation_type = '3_fold_stratified_cv'
        t_log.avg_precision, t_log.avg_recall, t_log.avg_fscore, t_log.avg_accuracy, t_log.avg_test_support, t_log.avg_train_support = cv_metrics
        t_log.support = self.X.shape[0]
        with transaction.manager:
            self.session.merge(t_log)

    def get_cv_metrics(self, cv):
        fold_avg_p = []
        fold_avg_r = []
        fold_avg_f1 = []
        fold_accuracy = []
        fold_test_support = []
        fold_train_support = []
        for i, (train, test) in enumerate(cv):
            train_df, train_y = self.X.iloc[train], self.y.iloc[train]
            test_df, test_y = self.X.iloc[test], self.y.iloc[test]
            estimator = clone(self.pipeline)
            estimator.fit(train_df, train_y)
            y_pred = estimator.predict(test_df)
            p, r, f1, s = precision_recall_fscore_support(test_y, y_pred)
            accuracy = accuracy_score(test_y, y_pred)
            # support weighted average precision,recall,f1,support across classes
            avg_p, avg_r, avg_f1 = (
                np.average(p, weights=s), np.average(r, weights=s), np.average(f1, weights=s))
            test_support = test_y.shape[0]
            train_support = train_y.shape[0]
            fold_avg_p.append(avg_p)
            fold_avg_r.append(avg_r)
            fold_avg_f1.append(avg_f1)
            fold_accuracy.append(accuracy)
            fold_test_support.append(test_support)
            fold_train_support.append(train_support)
        return np.average(fold_avg_p), np.average(fold_avg_r), np.average(fold_avg_f1), np.average(
            fold_accuracy), np.average(test_support), np.average(train_support)

    def fit(self, X, y):
        self.model = self.pipeline.fit(X, y)

    def predict(self, X):
        return self.pipeline.predict(X)

    def predict_proba(self, X):
        return self.pipeline.predict_proba(X)

    def save_model(self):
        serialized_model = '{}/category_group_{}_model.pkl'.format(self.model_path,
                                                                   self.category_group.category_group_id)
        joblib.dump(self.model, serialized_model, compress=1)
        self.training_log.serialized_model = serialized_model
        self.training_log.end_time = datetime.now()
        with transaction.manager:
            self.session.merge(self.training_log)

    def apply_model(self, sm_account_id):
        BATCH_SIZE = 10000
        self.logger.info("Starting model application for sm_account: {}".format(sm_account_id))
        self.load_model()
        model_application_log = ModelApplicationLog(sm_account_id=sm_account_id,
                                                    category_group_id=self.category_group.category_group_id,
                                                    model_id=self.training_log.id,
                                                    start_time=datetime.now()
                                                    )
        with transaction.manager:
            self.session.add(model_application_log)

        user = self.session.query(User).filter(User.user_email == 'system@sosilee.com').first()
        self.logger.info("querying unlabelled interactions...")
        unlabelled = self.session.query(Interactions.id, Interactions.message).filter(
            Interactions.sm_account_id == sm_account_id).filter(
            func.length(Interactions.message) > 0).filter(
            ~ exists().where(Interactions.id == InteractionCategory.interaction_id)).filter(
            ~ Interactions.is_page_post).yield_per(BATCH_SIZE)
        self.logger.info(unlabelled)
        interactions = []
        ids = []
        current_batch = 1
        processed_interactions = 0
        for i, row in enumerate(unlabelled):
            ids.append(row.id)
            interactions.append(row.message)
            if i % BATCH_SIZE == 0:
                self.logger.info("predicting categories for batch:{}".format(current_batch))
                self.predict_batch(ids, interactions, user, sm_account_id)
                interactions = []
                ids = []
                current_batch += 1
            processed_interactions += 1
        self.predict_batch(ids, interactions, user, sm_account_id)

        with transaction.manager:
            model_application_log.end_time = datetime.now()
            model_application_log.processed_interactions = processed_interactions
            self.session.merge(model_application_log)

    def predict_batch(self, ids, interactions, user, sm_account_id):
        if len(ids) > 0:
            predictions = self.pipeline.predict(interactions)
            interaction_categories = [{'interaction_id': id, 'category_id': int(category), 'user_id': user.user_id,
                                       'created_date': datetime.now(), 'sm_account_id': sm_account_id} for id, category
                                      in zip(ids, predictions)]
            self.engine.execute(InteractionCategory.__table__.insert(), interaction_categories)

    def load_model(self):
        self.training_log = self.session.query(ModelTrainingLog).filter(
            ModelTrainingLog.category_group_id == self.category_group.category_group_id).filter(
            ModelTrainingLog.end_time is not None).order_by(desc(ModelTrainingLog.end_time)).first()
        self.pipeline = joblib.load(self.training_log.serialized_model)
        self.logger.info('loaded model:{}'.format(self.training_log.serialized_model))
