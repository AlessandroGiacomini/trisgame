# -*- coding: utf-8 -*-`
"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""

import endpoints
from protorpc import remote, messages
from google.appengine.api import mail
from google.appengine.ext import ndb
from google.appengine.api import taskqueue
from models import User, Game, Score
from form import StringMessage, NewGameForm, GameForm, MakeMoveForm, \
        ScoreForms, GameForms, UserForm, UserForms
from utils import get_by_urlsafe, check_winner

NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(
        urlsafe_game_key=messages.StringField(1),)
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    MakeMoveForm,
    urlsafe_game_key=messages.StringField(1),)
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2))


@endpoints.api(name='tris', version='v1')
class TrisAPI(remote.Service):
    """Game API"""
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                'A User with that name already exists!')
        user = User(name=request.user_name, email=request.email)
        user.put()
        return StringMessage(message='User {} created!'.format(
            request.user_name))

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game"""

        userX = User.query(User.name == request.userX).get()
        userO = User.query(User.name == request.userO).get()

        # Check if userX exist
        if not userX:
            raise endpoints.NotFoundException(
                'A User with %s name does not exist!' % userX)
        # Check if userO exist
        if not userO
            raise endpoints.NotFoundException(
                'A User with %s name does not exist!' % userO)
        game = Game.new_game(userX.key, userO.key)
        return game.to_form()

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            return game.to_form()
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """Makes a move. Returns a game state with message"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game.boolCompleted:
            raise endpoints.NotFoundException('Game already over')

        # 01 Check the TURN
        user = User.query(User.name == request.user_name).get()
        if user.key != game.turnOf:
            raise endpoints.BadRequestException('It\'s not your turn!')
        if user.key == game.userX:
            x = True
        else:
            x = False

        # 02 Verify if MOVE is VALID insiede the board 3*3
        move = request.move
        board_size = 3
        size = 3 * 3 - 1 # Just to show the meaning of size 8
        if move < 0 or move > size:
            raise endpoints.BadRequestException('Invalid move! Must be between'
                                                '0 and %s ' % size)
        if game.board[move] != '':
            raise endpoints.BadRequestException('Invalid move!')


        # 03 SIGN THE BOARD
        if x:
          game.board[move] = 'X'
        else
          game.board[move] = 'O'

        # 04 Add the move to the HISTORY MOVES
        game.history.append(('X' if x else 'O', move))
        
        # 05 Decide the TURN
        if x:
          game.turnOf = game.userO
        else:
          game.turnOf = game.userX

        # 06 Check if there's a winner. If there is it end game else end game with draw
        winner = checkWinner(game.board)
        if winner:
            game.end_game(user.key)
        else:
            boolFull = True
            board = game.board
            for cell in board:
                  if not cell:
                      boolFull = False
                  break

            if boolFull:
                game.end_game()
        game.put()
        
        return game.to_form()

    @endpoints.method(response_message=ScoreForms,
                      path='scores',
                      name='get_scores',
                      http_method='GET')
    def get_scores(self, request):
        """Return all scores"""
        return ScoreForms(items=[score.to_form() for score in Score.query()])

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=ScoreForms,
                      path='scores/user/{user_name}',
                      name='get_user_scores',
                      http_method='GET')
    def get_user_scores(self, request):
        """Returns all of an individual User's scores"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                'A User with that name does not exist!')
        scores = Score.query(ndb.OR(Score.userX == user.key,
                                    Score.userO == user.key))
        return ScoreForms(items=[score.to_form() for score in scores])

    # 01 get_user_games
    # This returns all of a User's active games
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=GameForms,
                      path='user/games',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):

        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.BadRequestException('User not found!')
        
        games = Game.query(ndb.OR(Game.userX == user.key,
                                  Game.userO == user.key)). \
            filter(Game.boolCompleted == False)
        return GameForms(items=[game.to_form() for game in games])

    # 02 cancel_game
    # This endpoint allows users to cancel a game in progress
    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/{urlsafe_game_key}',
                      name='cancel_game',
                      http_method='DELETE')
    def cancel_game(self, request):
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game and not game.boolCompleted:
            game.key.delete()
            return StringMessage(message='Game with key: {} deleted.'.
                                 format(request.urlsafe_game_key))
        elif game and game.boolCompleted:
            raise endpoints.BadRequestException('Game is already over!')
        else:
            raise endpoints.NotFoundException('Game not found!')

    # 04 get_user_rankings
    # Returns all players ranked by points
    @endpoints.method(response_message=UserForms,
                      path='user/ranking',
                      name='get_user_rankings',
                      http_method='GET')
    def get_user_rankings(self, request):
        users = User.query(User.totalMatches > 0).fetch()
        users = sorted(users, key=lambda x: x.points, reverse=True)
        return UserForms(items=[user.to_form() for user in users])

    # 05 get_game_history
    # Return the history of moves for a TRIS game.
    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/{urlsafe_game_key}/history',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if not game:
            raise endpoints.NotFoundException('Game not found')
        return StringMessage(message=str(game.history))

api = endpoints.api_server([TrisAPI])
