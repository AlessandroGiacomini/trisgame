# Project: TRIS Game - Alessandro Giacomini

## Set-Up Instructions:
1.  Update the value of application in app.yaml to the app ID you have registered
in the App Engine admin console and would like to use to host your instance of this sample.
1.  Run the app with the devserver using dev_appserver.py DIR, and ensure it's
running by visiting your local server's address (by default localhost:8080.)
1.  (Optional) Generate your client library(ies) with the endpoints tool.
Deploy your application.

## Files Included:
- api.py: Contains endpoints and game playing logic.
- app.yaml: App configuration.
- cron.yaml: Cronjob configuration.
- main.py: Handler for taskqueue handler.
- models.py: Entity definitions and their helpful functions.
- utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.

## Game Description:
TRIS also known as Tic-tac-toe noughts and crosses or Xs and Os is a paper-and-pencil game for two players, X and O, who take turns marking the spaces in a 3×3 grid. The player who succeeds in placing three of their marks in a horizontal, vertical, or diagonal row wins the game.

Players soon discover that best play from both parties leads to a draw. Hence, Tic-tac-toe is most often played by young children.

Because of the simplicity of tic-tac-toe, it is often used as a pedagogical tool for teaching the concepts of good sportsmanship and the branch of artificial intelligence that deals with the searching of game trees. It is straightforward to write a computer program to play tic-tac-toe perfectly, to enumerate the 765 essentially different positions (the state space complexity), or the 26,830 possible games up to rotations and reflections (the game tree complexity) on this space.

The game can be generalized to an m,n,k-game in which two players alternate placing stones of their own color on an m×n board, with the goal of getting k of their own color in a row. Tic-tac-toe is the (3,3,3)-game.

More information about TRIS are available [here](https://en.wikipedia.org/wiki/Tic-tac-toe)

## API Game Description:

### Endpoints Included:
- **create_user**
- Path: 'user'
- Method: POST
- Parameters: user_name, email
- Returns: Message confirming creation of the User.
- Description: Creates a new User. user_name provided must be unique. Will raise a ConflictException if a User with that user_name already exists.

- **new_game**
- Path: 'game'
- Method: POST
- Parameters: userX, userY
- Returns: GameForm with initial game state.
- Description: Creates a new Game.

- **get_game**
- Path: 'game/{urlsafe_game_key}'
- Method: GET
- Parameters: urlsafe_game_key
- Returns: GameForm with current game state.
- Description: Returns the current state of a game.

- **make_move**
- Path: 'game/{urlsafe_game_key}'
- Method: PUT
- Parameters: urlsafe_game_key, user_name, move
- Returns: GameForm with new game state.
- Description: 
1. Check the TURN
2. Verify if MOVE is VALID
3. SIGN THE BOARD
4. Add the move to the HISTORY MOVES
5. Check if there's a winner and in case end game else end game

- **get_scores**
- Path: 'scores'
- Method: GET
- Parameters: None
- Returns: ScoreForms.
- Description: Returns all Scores in the database (unordered).

- **get_user_scores**
- Path: 'scores/user/{user_name}'
- Method: GET
- Parameters: user_name
- Returns: ScoreForms.
- Description: Returns all Scores recorded by the provided player (unordered).
Will raise a NotFoundException if the User does not exist.

- **get_user_games**
- Path: 'user/games'
- Method: GET
- Parameters: user_name, email
- Returns: GameForms
- Description: Return all User's active games.

- **cancel_game**
- Path: 'game/{urlsafe_game_key}'
- Method: DELETE
- Parameters: urlsafe_game_key
- Returns: StringMessage
- Description: Allows users to cancel a game in progress.

- **get_user_rankings**
- Path: 'user/ranking'
- Method: GET
- Parameters: None
- Returns: UserForms sorted by points.
- Description: Returns all players ranked by points.

- **get_game_history**
- Path: 'game/{urlsafe_game_key}/history'
- Method: GET
- Parameters: urlsafe_game_key
- Returns: StringMessage
- Description: Return the history of moves for a TRIS game.

### Models Included:
- **User**
- Stores unique user_name and (optional) email address.

- **Game**
- Stores unique game states. Associated with User models via KeyProperties
userX and userO.

- **Score**
- Records completed games. Associated with Users model via KeyProperty.

### Forms Included:
- **GameForm**
- Representation of a Game's state (urlsafe_key, board, sizeBoard,
userX, userO, turnOf, boolCompleted, winner, draw).
- **GameForms**
- Multiple GameForm container.
- **NewGameForm**
- Used to create a new game (userX, userO)
- **MakeMoveForm**
- Inbound make move form (user_name, move).
- **ScoreForm**
- Representation of a completed game's Score.
- **ScoreForms**
- Multiple ScoreForm container.
- **UserForm**
- Representation of a User.
- **UserForms**
- Multiple UserForm Container.
- **StringMessage**
- General purpose String container.

### Citations
Udacity forums and StackOverflow forums.
