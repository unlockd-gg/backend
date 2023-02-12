import logging
import random

def weighted_choice(object_list):
    """ we need a selectionProbability field """
    choices = []
    for i, objecti in enumerate(object_list):
        logging.info('adding choice to list')
        choice= [ objecti, objecti.selectionProbability, i ]
        choices.append(choice)

    total = sum(w for c, w, indexi in choices)
    logging.info('total: %s' %total)
    r = random.uniform(0, total)
    upto = 0
    for c, w, indexi in choices:
        logging.info('c: %s' %c)
        logging.info('w: %s' %w)
        logging.info('indexi: %s' %indexi)
        logging.info('choosing...')
        if upto + w >= r:
            return c, indexi
        upto += w
    assert False, "Shouldn't get here"
