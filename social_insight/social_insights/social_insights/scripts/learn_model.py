import os
import sys
import logging

from pyramid.paster import (
    get_appsettings,
    setup_logging,
)
from pyramid.scripts.common import parse_vars

from ..categorization_model import CategorizationModel
from ..models import (
    DBSession,
    CategoryGroup)
from ..utils import configure_db_session


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
    model_path = settings['categorization_models.model_path']
    new_labelled_threshold = int(settings['categorization_models.new_labelled_threshold'])
    logger = logging.getLogger(__name__)

    category_groups = DBSession.query(CategoryGroup).all()
    for group in category_groups:
        logger.info("Training model for category group:{}".format(group.name))
        CategorizationModel(group, engine, session, model_path, new_labelled_threshold)
