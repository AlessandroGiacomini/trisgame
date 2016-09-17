"""utils.py - File for collecting general utility functions."""

import logging
from google.appengine.ext import ndb
import endpoints

def get_by_urlsafe(urlsafe, model):
    """Returns an ndb.Model entity that the urlsafe key points to. Checks
        that the type of entity returned is of the correct kind. Raises an
        error if the key String is malformed or the entity is of the incorrect
        kind
    Args:
        urlsafe: A urlsafe key string
        model: The expected entity kind
    Returns:
        The entity that the urlsafe Key string points to or None if no entity
        exists.
    Raises:
        ValueError:"""
    try:
        key = ndb.Key(urlsafe=urlsafe)
    except TypeError:
        raise endpoints.BadRequestException('Invalid Key')
    except Exception, e:
        if e.__class__.__name__ == 'ProtocolBufferDecodeError':
            raise endpoints.BadRequestException('Invalid Key')
        else:
            raise

    entity = key.get()
    if not entity:
        return None
    if not isinstance(entity, model):
        raise ValueError('Incorrect Kind')
    return entity


def checkWinner(board, size=3):
    """Check if there is a winner"""
    for i in range(size):
        if board[size * i]:
            itemsOnRows = board[size * i:size * i + size]
            #  Check if all items on a row in list have the same value
            if (all(x == itemsOnRows[0] for x in itemsOnRows)):
                return board[size * i]
    for i in range(size):
        if board[i]:
            itemsOnColumns = board[i:size * size:size]
            #  Check if all items on a column in list have the same value
            if (all(x == itemsOnColumns[0] for x in itemsOnColumns)):
                return board[i]
    if board[0]:
        itemsOnDiagonals = board[0:size * size:size + 1]
        #  Check if all items on a diagonal in list have the same value
        if all(x == itemsOnDiagonals[0] for x in itemsOnDiagonals):
            return board[0]
    if board[size - 1]:
        items = board[size - 1:size * (size - 1) + 1:size - 1]
        if all(x == items[0] for x in items):
            return board[size - 1]