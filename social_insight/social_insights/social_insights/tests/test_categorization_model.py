import transaction
import logging
import os
import pandas as pd
from pyramid.paster import (
    get_appsettings
)
from unittest import TestCase
from datetime import datetime
from social_insights.categorization_model import CategorizationModel
from social_insights.utils import configure_db_session, drop_all_tables
from social_insights.models import (
    CategoryGroup,
    Category,
    User,
    Interactions,
    InteractionCategory,
    ModelTrainingLog,
    SmAccounts,
    ModelApplicationLog)

from nose.tools import ok_, eq_


class TestCategorizationModel(TestCase):
    def load_data(self, file_name):
        test_data = pd.read_csv(os.getcwd() + '/{}'.format(file_name))
        # Preparing data for flow 1 and 2
        with transaction.manager:
            self.session.merge(CategoryGroup(category_group_id=0, name='test_category'))
            self.session.merge(SmAccounts(sm_account_id=12345))
            self.session.merge(SmAccounts(sm_account_id=12346))
            self.category_group_details = self.session.query(CategoryGroup).filter(
                CategoryGroup.name == 'test_category').first()
            self.session.merge(Category(category_id=1, name='Complaint', category_group=self.category_group_details))
            self.session.merge(Category(category_id=2, name='Others', category_group=self.category_group_details))
            self.session.merge(Category(category_id=3, name='New', category_group=self.category_group_details))
            self.session.merge(User(user_id=1, user_email='system@sosilee.com', fb_user_name='system'))
            self.session.merge(User(user_id=2, user_email='testuser@sosilee.com', fb_user_name='test_user'))
        with transaction.manager:
            for index, rows in test_data.iterrows():
                self.session.merge(Interactions(id=str(rows['id']), message=rows['message'],
                                                is_page_post=str(rows['is_page_post']), like_count=rows['like_count'],
                                                parent_id=rows['parent_id'], created_date=rows['created_date'],
                                                sm_account_id=rows['sm_account_id']))

        with transaction.manager:
            user_details = self.session.query(User).filter(User.user_email == "testuser@sosilee.com").first()
            labelled_test_data = test_data.dropna(subset=['is_complaint'])
            for index, rows in labelled_test_data.iterrows():
                complaint = self.session.query(Category). \
                    filter((Category.name == str(rows['is_complaint'])) &
                           (Category.category_group_id == self.category_group_details.category_group_id)).first()
                record = InteractionCategory(user_id=user_details.user_id,
                                             interaction_id=str(rows['id']),
                                             category_id=complaint.category_id,
                                             sm_account_id=rows['sm_account_id'],
                                             created_date=datetime.now())
                self.session.merge(record)

    def test_categorization_model(self):
        settings = get_appsettings(os.getcwd() + '/test.ini')
        self.engine, self.session = configure_db_session(settings)

        try:
            self.logger = logging.getLogger('social_insights')
            self.logger.setLevel(logging.DEBUG)
            self.logger.info('The session is {}'.format(self.session))
            self.logger.info('The engine is {}'.format(self.engine))
            self.model_path = settings['categorization_models.model_path']
            new_labelled_threshold = int(settings['categorization_models.new_labelled_threshold'])

            # checking default model_path and new_labelled_threshold
            eq_(self.model_path, '/tmp', "Model path does not match expected path")
            eq_(new_labelled_threshold, 100, "Configured threshold do not match expected")

            self.logger.info('running setUp...............................')

            # Calling test case 1
            self.train_model_with_labelled_interactions()
            # Calling test case 2
            self.apply_model_for_unlabelled_interactions()
            # Calling test case 3
            self.retrain_model_with_new_interactions()
            # Calling test case 4
            self.apply_retrained_model_to_new_interactions()

        except Exception as e:
            self.logger.exception(e)
            self.fail('Test case failed')

        finally:
            # drop tables
            self.session.close()
            drop_all_tables(settings)

    def train_model_with_labelled_interactions(self):
        # TestCase 1: Checking whether the model is being trained with labelled sample available
        self.load_data('test_data.csv')
        time_for_test1 = datetime.now()
        self.cm = CategorizationModel(self.category_group_details, self.engine, self.session, self.model_path, 20)
        eq_(self.cm.new_labelled_threshold, 20, "Configured threshold do not match expected")

        training_log_details = self.session.query(ModelTrainingLog). \
            filter((ModelTrainingLog.category_group_id == 0) &
                   (ModelTrainingLog.start_time >= time_for_test1)).first()
        eq_(training_log_details.category_group_id, 0, "Category_group_id do not match expected")
        eq_(training_log_details.validation_type, '3_fold_stratified_cv', "Validation type do not match expected")
        ok_(0 <= training_log_details.avg_precision <= 1, "Average precision is not in-between 0 and 1")
        ok_(0 <= training_log_details.avg_recall <= 1, "Average recall is not in-between 0 and 1")
        ok_(0 <= training_log_details.avg_fscore <= 1, "Average f-score is not in-between 0 and 1")
        ok_(0 <= training_log_details.avg_accuracy <= 1, "Average accuracy is not in-between 0 and 1")
        ok_(training_log_details.avg_test_support <= 24, "Test support does not match in flow 1")
        ok_(training_log_details.avg_train_support <= 24, "Train support does not match in flow 1")
        eq_(training_log_details.serialized_model, '/tmp/category_group_0_model.pkl',
            "Model name do not match expected")
        ok_(training_log_details.end_time >= training_log_details.start_time,
            "End time is lesser than start time")
        self.logger.info('Test case 1 : train model with labelled interactions passed... Moving on to Test case 2...')

    def apply_model_for_unlabelled_interactions(self):
        # Test Case 2: Checking whether model is applied to unlabelled interactions
        time_for_test2 = datetime.now()
        category_groups = self.session.query(CategoryGroup).all()
        for sm_account in self.session.query(SmAccounts):
            for cg in category_groups:
                CategorizationModel.apply(cg, self.engine, self.session, sm_account_id=sm_account.sm_account_id)

        application_log_details = self.session.query(ModelApplicationLog). \
            filter((ModelApplicationLog.processed_interactions > 0) &
                   (ModelApplicationLog.category_group_id == 0) &
                   (ModelApplicationLog.start_time >= time_for_test2) &
                   (ModelApplicationLog.sm_account_id == 12345)).first()

        eq_(application_log_details.processed_interactions, 6,
            "Number of interactions predicted do not match expected")
        ok_(application_log_details.end_time >= application_log_details.start_time,
            "End time is lesser than start time")

        application_log_details = self.session.query(ModelApplicationLog). \
            filter((ModelApplicationLog.processed_interactions > 0) &
                   (ModelApplicationLog.category_group_id == 0) &
                   (ModelApplicationLog.start_time >= time_for_test2) &
                   (ModelApplicationLog.sm_account_id == 12346)).first()

        eq_(application_log_details.processed_interactions, 7,
            "Number of interactions predicted do not match expected")
        ok_(application_log_details.end_time >= application_log_details.start_time,
            "End time is lesser than start time")
        self.logger.info('Test case 2 : apply model for unlabelled interactions passed... Moving on to Test case 3...')

    def retrain_model_with_new_interactions(self):
        # Test Case 3: Checking whether model is retraining with new labelled interactions
        self.load_data('test_data1.csv')
        time_for_test3 = datetime.now()
        self.cm = CategorizationModel(self.category_group_details, self.engine, self.session, self.model_path, 20)

        self.assertEqual(self.cm.new_labelled_threshold, 20)
        training_log_details = self.session.query(ModelTrainingLog). \
            filter((ModelTrainingLog.category_group_id == 0) &
                   (ModelTrainingLog.start_time >= time_for_test3)).first()
        eq_(training_log_details.category_group_id, 0, "Category_group_id do not match expected")
        eq_(training_log_details.validation_type, '3_fold_stratified_cv', "Validation type do not match expected")
        ok_(0 <= training_log_details.avg_precision <= 1, "Average precision is not in-between 0 and 1")
        ok_(0 <= training_log_details.avg_recall <= 1, "Average recall is not in-between 0 and 1")
        ok_(0 <= training_log_details.avg_fscore <= 1, "Average f-score is not in-between 0 and 1")
        ok_(0 <= training_log_details.avg_accuracy <= 1, "Average accuracy is not in-between 0 and 1")
        ok_(training_log_details.avg_test_support <= 33, "Test support does not match in flow 2")
        ok_(training_log_details.avg_train_support <= 33, "Train support does not match in flow 2")
        eq_(training_log_details.serialized_model, '/tmp/category_group_0_model.pkl',
            "Model name do not match expected")
        ok_(training_log_details.end_time >= training_log_details.start_time,
            "End time is lesser than start time")
        self.logger.info('Test case 3 : retrain model with new interactions passed... Moving on to Test case 4...')

    def apply_retrained_model_to_new_interactions(self):
        # Test Case 4: Checking whether latest model is applied for new unlabelled interactions
        time_for_test4 = datetime.now()
        category_groups = self.session.query(CategoryGroup).all()
        for sm_account in self.session.query(SmAccounts):
            for cg in category_groups:
                CategorizationModel.apply(cg, self.engine, self.session, sm_account_id=sm_account.sm_account_id)

        application_log_details = self.session.query(ModelApplicationLog). \
            filter((ModelApplicationLog.processed_interactions > 0) &
                   (ModelApplicationLog.category_group_id == 0) &
                   (ModelApplicationLog.start_time >= time_for_test4)&
                   (ModelApplicationLog.sm_account_id == 12345)).first()

        eq_(application_log_details.processed_interactions, 6,
            "Number of interactions predicted do not match expected")
        ok_(application_log_details.end_time >= application_log_details.start_time,
            "End time is lesser than start time")

        application_log_details = self.session.query(ModelApplicationLog). \
            filter((ModelApplicationLog.processed_interactions > 0) &
                   (ModelApplicationLog.category_group_id == 0) &
                   (ModelApplicationLog.start_time >= time_for_test4) &
                   (ModelApplicationLog.sm_account_id == 12346)).first()

        eq_(application_log_details.processed_interactions, 6,
            "Number of interactions predicted do not match expected")
        ok_(application_log_details.end_time >= application_log_details.start_time,
            "End time is lesser than start time")
        self.logger.info('Test case 4 : apply retrained model to new interactions passed...')
        self.logger.info('All tests completed successfully...')
