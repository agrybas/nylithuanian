#encoding=utf-8

import nylithuanian.settings as settings
from django.core.exceptions import ValidationError

import logging

if settings.DEBUG:
    logger = logging.getLogger('debug.' + __name__)
else:
    logger = logging.getLogger('production.' + __name__)


def validate_uncommon_word(uncommon_word):
    """
    Validates that the provided word is not in a common-word list.
    """
    
    logger.info('Starting uncommon word validation...')
    logger.debug('Loading common-word dictionary from {0}'.format(settings.STATIC_ROOT + 'passwords/common.txt'))
    
    with open(settings.STATIC_ROOT + 'passwords/common.txt', mode='rU') as f:
        for common_word in f:
            common_word = common_word.rstrip('\n')
            if uncommon_word.lower() == common_word.lower():          
                logger.info('Supplied word found in common-word dictionary.')
                raise ValidationError('Jūsų įvestas žodis rastas dažnai pasitaikančių žodžių sąraše.')
    logger.info('Word not found in common-word dictionary.')
    
    