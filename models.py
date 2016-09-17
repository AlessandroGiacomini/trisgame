"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb
from protorpc import messages


class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    totalMatches = ndb.IntegerProperty(default=0)
    winnings = ndb.IntegerProperty(default=0)
    losses = ndb.IntegerProperty(default=0)
    draws = ndb.IntegerProperty(default=0)

    def updateUser(self):
        """Adds match to user and update."""
        self.total_played += 1
        self.put()

    def add_win(self):
        """Add a winning"""
        self.winnings += 1
        self.updateUser()

    def add_draw(self):
        """Add a draw"""
        self.draws += 1
        self.updateUser()

    def add_loss(self):
        """Add a loss"""
        self.losses += 1
        self.updateUser()

    @property
    def points(self):
        """Points of a User"""
        return self.wins*3+self.draws+self.losses*(-2)

    def to_form(self):
        """Returns a form representation of the user"""
        form = UserForm()
        form.name = self.key.name
        form.email = self.email
        form.totalMatches = self.totalMatches
        form.winnings = self.winnings
        form.losses = self.losses
        form.draws = self.draws
        form.points = self.points
        return form


class UserForm(messages.Message):
    """User Form"""
    name = messages.StringField(1, required=True)
    email = messages.StringField(2)
    totalMatches = messages.IntegerField(3, required=True)
    winnings = messages.IntegerField(4, required=True)
    losses = messages.IntegerField(5, required=True)
    draws = messages.IntegerField(6, required=True)
    points = messages.IntegerField(7)


class UserForms(messages.Message):
    """Container for multiple User Forms"""
    items = messages.MessageField(UserForm, 1, repeated=True)


class Game(ndb.Model):
    """Game object"""
    board = ndb.PickleProperty(required=True)
    sizeBoard = ndb.IntegerProperty(required=True, default=3)
    turnOf = ndb.KeyProperty(required=True)
    userX = ndb.KeyProperty(required=True, kind='User')
    userO = ndb.KeyProperty(required=True, kind='User')
    boolCompleted = ndb.BooleanProperty(required=True, default=False)
    winner = ndb.KeyProperty()
    draw = ndb.BooleanProperty(default=False)
    history = ndb.PickleProperty(required=True)

    @classmethod
    def new_game(class, userX, userO):
        """Returns a new game"""
        game = Game(userX=userX,
                    userO=userO,
                    turnOf=userX)
        game.board = ['' for _ in range(3*3)]
        game.history = []
        game.sizeBoard = 3
        game.put()
        return game

    def to_form(self):
        """Returns a form representation of the game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.board = str(self.board)
        form.sizeBoard = 3
        form.userX = self.userX
        form.userO = self.userO
        form.turnOf = self.turnOf
        form.boolCompleted = self.boolCompleted
        return form

        if self.winner:
            form.winner = self.winner.get().name
        if self.draw:
            form.draw = self.draw
        return form

    def end_game(self, winner=None):
        """Ends the game"""
        self.boolCompleted = True
        if winner:
            self.winner = winner
        else:
            self.draw = True
        self.put()

        if winner:
            result = 'userX' if winner == self.userX else 'userO'
        else:
            result = 'draw'

        score = Score(date=date.today(),
                      userX=self.userX,
                      userO=self.userO,
                      result=result)
        score.put()

        if winner:
            winner.get().add_win()
            loser = self.userX
            if winner == self.userO else self.userO
            loser.get().add_loss()
        else:
            self.userX.get().add_draw()
            self.userO.get().add_draw()


class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    board = messages.StringField(2, required=True)
    sizeBoard = messages.IntegerField(3, required=True)
    userX = messages.StringField(4, required=True)
    userO = messages.StringField(5, required=True)
    turnOf = messages.StringField(6, required=True)
    boolCompleted = messages.BooleanField(7, required=True)
    winner = messages.StringField(8)
    draw = messages.BooleanField(9)


class GameForms(messages.Message):
    """Container for multiple GameForm"""
    items = messages.MessageField(GameForm, 1, repeated=True)


class NewGameForm(messages.Message):
    """Create a new game"""
    userX = messages.StringField(1, required=True)
    userO = messages.StringField(2, required=True)


class Score(ndb.Model):
    """Score object"""
    date = ndb.DateProperty(required=True)
    userX = ndb.KeyProperty(required=True)
    userO = ndb.KeyProperty(required=True)
    result = ndb.StringProperty(required=True)

    def to_form(self):
        form = ScoreForm()
        form.date = str(self.date)
        form.userX = str(self.userX)
        form.userO = self.userO
        form.result = self.result
        return form


class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    date = messages.StringField(1, required=True)
    userX = messages.StringField(2, required=True)
    userO = messages.StringField(3, required=True)
    result = messages.StringField(4)


class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)


class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    user_name = messages.StringField(1, required=True)
    move = messages.IntegerField(2, required=True)


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)
