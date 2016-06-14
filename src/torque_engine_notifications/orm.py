# -*- coding: utf-8 -*-

"""Model classes encapsulating ``Notification``s, their ``Dispatch``
  and a user's notification ``Preferences``.
"""

__all__ = [
    'Dispatch',
    'Notification',
    'Preferences',
]

import os

from datetime import datetime

from sqlalchemy import orm
from sqlalchemy import schema
from sqlalchemy import types

import pyramid_basemodel as bm

from . import constants

class Preferences(bm.Base, bm.BaseMixin):
    """Encapsulate a user's notification preferences."""

    __tablename__ = 'notification_preferences'

    # Belongs (one-to-one) to a user.
    user_id = schema.Column(
        types.Integer,
        schema.ForeignKey('auth_users.id'),
        nullable=False,
    )
    user = orm.relationship(
        'pyramid_simpleauth.model.User',
        single_parent=True,
        backref=orm.backref(
            'preferences',
            single_parent=True,
            uselist=False,
        )
    )

    # Record the channel they'd like to be notified through and how
    # often they want to be notified.
    channel = schema.Column(
        types.Unicode(6),
        default=constants['email'],
        nullable=False,
    )
    frequency = schema.Column(
        types.Unicode(96),
        default=constants['immediately'],
        nullable=False,
    )

    # Flag properties.
    def disabled(self):
        return self.frequency == constants.FREQUENCIES['never']

    def enabled(self):
        return not self.enabled

    def send_immediately(self):
        return self.frequency == constants.FREQUENCIES['immediately']

class Notification(bm.Base, bm.BaseMixin):
    """Notify a user about an event."""

    __tablename__ = 'notifications'

    # Notify a user.
    user_id = schema.Column(
        types.Integer,
        schema.ForeignKey('auth_users.id'),
        nullable=False,
    )
    user = orm.relationship(
        'pyramid_simpleauth.model.User',
        backref=orm.backref(
            'notifications,
            single_parent=True,
        )
    )

    # About an event.
    event_id = schema.Column(
        types.Integer,
        schema.ForeignKey('activity_events.id'),
        nullable=False,
    )
    event = orm.relationship(
        'pyramid_torque_engine.orm.ActivityEvent',
        backref=orm.backref(
            'notifications,
            single_parent=True,
        ),
    )

    # Record the role that the user matched when creating this
    # notification. This allows template rendering to adapt
    # according to the role *and* for the dispatch mapping to
    # be registered against the `interface, event, role` and
    # then looked up by `context, event, role` at spawn time so
    # that we *always spawn dispatches with the latest config*.
    role = schema.Column(
        types.Unicode(64),
    )

    # When is this notification due to be spawned?
    due = schema.Column(
        types.DateTime,
        nullable=False,
    )

    # When *was* it spawned?
    spawned = schema.Column(
        types.DateTime,
    )

    # Potentially record when it was read. (Notifications that are read before
    # they're spawned need not be dispatched -- because the user has already
    # seen them).
    read = schema.Column(
        types.DateTime,
    )

class Dispatch(bm.Base, bm.BaseMixin):
    """Encapsulate the dispatch of a notification."""

    __tablename__ = 'notification_dispatches'

    # Belongs to a notification.
    notification_id = schema.Column(
        types.Integer,
        schema.ForeignKey('notifications.id'),
        nullable=False,
    )
    notification = orm.relationship(
        Notification,
        backref=orm.backref(
            'dispatches',
            single_parent=True,
        )
    )

    # How should it be sent?
    channel = schema.Column(
        types.Unicode(6),
        nullable=False
    )
    view = schema.Column(
        types.Unicode(128),
    )
    spec = schema.Column(
        types.Unicode(255),
    )
    batch_spec = schema.Column(
        types.Unicode(255),
    )

    # To whom? Note that these can be email, phone number -- whatever
    # primary identifier the channel requires.
    to_address = schema.Column(
        types.Unicode(255),
    )
    bcc_address = schema.Column(
        types.Unicode(255),
    )

    # When was it sent?
    sent = schema.Column(
        types.DateTime,
    )
