"""
The turtle_adventure module maintains all classes related to the Turtle's
adventure game.
"""
from turtle import RawTurtle
from gamelib import Game, GameElement
import random


class TurtleGameElement(GameElement):
    """
    An abstract class representing all game elemnets related to the Turtle's
    Adventure game
    """

    def __init__(self, game: "TurtleAdventureGame"):
        super().__init__(game)
        self.__game: "TurtleAdventureGame" = game

    @property
    def game(self) -> "TurtleAdventureGame":
        """
        Get reference to the associated TurtleAnvengerGame instance
        """
        return self.__game


class Waypoint(TurtleGameElement):
    """
    Represent the waypoint to which the player will move.
    """

    def __init__(self, game: "TurtleAdventureGame"):
        super().__init__(game)
        self.__id1: int
        self.__id2: int
        self.__active: bool = False

    def create(self) -> None:
        self.__id1 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")
        self.__id2 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")

    def delete(self) -> None:
        self.canvas.delete(self.__id1)
        self.canvas.delete(self.__id2)

    def update(self) -> None:
        # there is nothing to update because a waypoint is fixed
        pass

    def render(self) -> None:
        if self.is_active:
            self.canvas.itemconfigure(self.__id1, state="normal")
            self.canvas.itemconfigure(self.__id2, state="normal")
            self.canvas.tag_raise(self.__id1)
            self.canvas.tag_raise(self.__id2)
            self.canvas.coords(self.__id1, self.x-10, self.y-10, self.x+10, self.y+10)
            self.canvas.coords(self.__id2, self.x-10, self.y+10, self.x+10, self.y-10)
        else:
            self.canvas.itemconfigure(self.__id1, state="hidden")
            self.canvas.itemconfigure(self.__id2, state="hidden")

    def activate(self, x: float, y: float) -> None:
        """
        Activate this waypoint with the specified location.
        """
        self.__active = True
        self.x = x
        self.y = y

    def deactivate(self) -> None:
        """
        Mark this waypoint as inactive.
        """
        self.__active = False

    @property
    def is_active(self) -> bool:
        """
        Get the flag indicating whether this waypoint is active.
        """
        return self.__active


class Home(TurtleGameElement):
    """
    Represent the player's home.
    """

    def __init__(self, game: "TurtleAdventureGame", pos: tuple[int, int], size: int):
        super().__init__(game)
        self.__id: int
        self.__size: int = size
        x, y = pos
        self.x = x
        self.y = y

    @property
    def size(self) -> int:
        """
        Get or set the size of Home
        """
        return self.__size

    @size.setter
    def size(self, val: int) -> None:
        self.__size = val

    def create(self) -> None:
        self.__id = self.canvas.create_rectangle(0, 0, 0, 0, outline="brown", width=2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)

    def update(self) -> None:
        # there is nothing to update, unless home is allowed to moved
        pass

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size/2,
                           self.y - self.size/2,
                           self.x + self.size/2,
                           self.y + self.size/2)

    def contains(self, x: float, y: float):
        """
        Check whether home contains the point (x, y).
        """
        x1, x2 = self.x-self.size/2, self.x+self.size/2
        y1, y2 = self.y-self.size/2, self.y+self.size/2
        return x1 <= x <= x2 and y1 <= y <= y2


class Player(TurtleGameElement):
    """
    Represent the main player, implemented using Python's turtle.
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 turtle: RawTurtle,
                 speed: float = 5):
        super().__init__(game)
        self.__speed: float = speed
        self.__turtle: RawTurtle = turtle

    def create(self) -> None:
        turtle = RawTurtle(self.canvas)
        turtle.getscreen().tracer(False) # disable turtle's built-in animation
        turtle.shape("turtle")
        turtle.color("green")
        turtle.penup()

        self.__turtle = turtle

    @property
    def speed(self) -> float:
        """
        Give the player's current speed.
        """
        return self.__speed

    @speed.setter
    def speed(self, val: float) -> None:
        self.__speed = val

    def delete(self) -> None:
        pass

    def update(self) -> None:
        # check if player has arrived home
        if self.game.home.contains(self.x, self.y):
            self.game.game_over_win()
        turtle = self.__turtle
        waypoint = self.game.waypoint
        if self.game.waypoint.is_active:
            turtle.setheading(turtle.towards(waypoint.x, waypoint.y))
            turtle.forward(self.speed)
            if turtle.distance(waypoint.x, waypoint.y) < self.speed:
                waypoint.deactivate()

    def render(self) -> None:
        self.__turtle.goto(self.x, self.y)
        self.__turtle.getscreen().update()

    # override original property x's getter/setter to use turtle's methods
    # instead
    @property
    def x(self) -> float:
        return self.__turtle.xcor()

    @x.setter
    def x(self, val: float) -> None:
        self.__turtle.setx(val)

    # override original property y's getter/setter to use turtle's methods
    # instead
    @property
    def y(self) -> float:
        return self.__turtle.ycor()

    @y.setter
    def y(self, val: float) -> None:
        self.__turtle.sety(val)


class Enemy(TurtleGameElement):
    def __init__(self, game: "TurtleAdventureGame", size: int, color: str, shape="oval"):
        super().__init__(game)
        self.size = size
        self.color = color
        self.shape = shape
        self.canvas_item = None

        self.x = random.randint(self.size, self.game.screen_width - self.size)
        self.y = random.randint(self.size, self.game.screen_height - self.size)

    def create(self):
        if self.shape == "oval":
            self.canvas_item = self.game.canvas.create_oval(
                self.x - self.size, self.y - self.size,
                self.x + self.size, self.y + self.size,
                fill=self.color
            )
        elif self.shape == "rectangle":
            self.canvas_item = self.game.canvas.create_rectangle(
                self.x - self.size, self.y - self.size,
                self.x + self.size, self.y + self.size,
                outline=self.color, width=2
            )

    def render(self):
        """Update the enemy's position on the canvas."""
        if self.canvas_item is not None:
            self.game.canvas.coords(
                self.canvas_item,
                self.x - self.size, self.y - self.size,
                self.x + self.size, self.y + self.size
            )

    def delete(self):
        if self.canvas_item is not None:
            self.game.canvas.delete(self.canvas_item)
            self.canvas_item = None

    def hits_player(self):
        player = self.game.player
        return (
            (self.x - self.size/2 < player.x < self.x + self.size/2) and
            (self.y - self.size/2 < player.y < self.y + self.size/2)
        )

class DemoEnemy(Enemy):
    """
    Demo enemy
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game, size, color)
        self.size = 20
        self.color = 'red'
        # Start at a random position in the game area
        self.x = random.randint(self.size, self.game.screen_width - self.size)
        self.y = random.randint(self.size, self.game.screen_height - self.size)
        # Move at a constant velocity
        self.velocity_x = random.choice([-1, 1]) * 5
        self.velocity_y = random.choice([-1, 1]) * 5
        # The canvas object for this enemy, to be created in the create method
        self.canvas_item = None

    def create(self):
        self.canvas_item = self.game.canvas.create_rectangle(
            self.x - self.size, self.y - self.size,
            self.x + self.size, self.y + self.size,
            fill=self.color)

    def update(self):
        # Update the enemy's position based on its velocity
        self.x += self.velocity_x
        self.y += self.velocity_y
        # Reverse direction if it hits the boundaries of the game area
        if not (self.size <= self.x <= self.game.screen_width - self.size):
            self.velocity_x = -self.velocity_x
        if not (self.size <= self.y <= self.game.screen_height - self.size):
            self.velocity_y = -self.velocity_y

    def delete(self):
        # Remove the rectangle from the canvas
        self.game.canvas.delete(self.canvas_item)

    def hits_player(self):
        """
        Check whether the enemy is hitting the player.
        Assumes both player and enemy are circular for simplicity.
        """
        player = self.game.player
        distance = ((self.x - player.x) ** 2 + (self.y - player.y) ** 2) ** 0.5
        return distance < (self.size + player.size) / 2

class EnemyGenerator:
    """
    An EnemyGenerator instance is responsible for creating enemies of various
    kinds and scheduling them to appear at certain points in time.
    """

    def __init__(self, game: "TurtleAdventureGame", level: int):
        self.game = game
        self._level = level
        self.schedule_enemy_creation()

    @property
    def level(self) -> int:
        """
        Get the game level.
        """
        return self._level

    @level.setter
    def level(self, value: int):
        """
        Set the game level.
        """
        self._level = value

    def schedule_enemy_creation(self):
        """
        Schedules the creation of enemies based on the current game level.
        """
        interval = max(1000 - (self.level * 100), 300)
        self.game.after(interval, self.create_enemy)

    def create_enemy(self):
        """
        Creates an enemy and adds it to the game. The type of enemy can be based on the level.
        """
        if self.level < 5:
            enemy = RandomWalkEnemy(self.game, size=20, color='red')
        elif self.level < 10:
            enemy = ChasingEnemy(self.game, size=20, color='blue')
        else:
            enemy = StealthEnemy(self.game, size=20, color='green')
        
        enemy.create()
        self.game.add_enemy(enemy)
        self.schedule_enemy_creation()


class TurtleAdventureGame(Game): # pylint: disable=too-many-ancestors
    """
    The main class for Turtle's Adventure.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self, parent, screen_width: int, screen_height: int, level: int = 1):
        self.level: int = level
        self.screen_width: int = screen_width
        self.screen_height: int = screen_height
        self.waypoint: Waypoint
        self.player: Player
        self.home: Home
        self.enemies: list[Enemy] = []
        self.enemy_generator: EnemyGenerator
        super().__init__(parent)

    def init_game(self):
        self.canvas.config(width=self.screen_width, height=self.screen_height)
        turtle = RawTurtle(self.canvas)
        # set turtle screen's origin to the top-left corner
        turtle.screen.setworldcoordinates(0, self.screen_height-1, self.screen_width-1, 0)

        self.waypoint = Waypoint(self)
        self.add_element(self.waypoint)
        self.home = Home(self, (self.screen_width-100, self.screen_height//2), 20)
        self.add_element(self.home)
        self.player = Player(self, turtle)
        self.add_element(self.player)
        self.canvas.bind("<Button-1>", lambda e: self.waypoint.activate(e.x, e.y))

        self.enemy_generator = EnemyGenerator(self, self.level)

        self.player.x = 50
        self.player.y = self.screen_height//2

    def add_enemy(self, enemy: Enemy) -> None:
        """
        Add a new enemy into the current game
        """
        self.enemies.append(enemy)
        self.add_element(enemy)

    def game_over_win(self) -> None:
        """
        Called when the player wins the game and stop the game
        """
        self.stop()
        font = ("Arial", 36, "bold")
        self.canvas.create_text(self.screen_width/2,
                                self.screen_height/2,
                                text="You Win",
                                font=font,
                                fill="green")

    def game_over_lose(self) -> None:
        """
        Called when the player loses the game and stop the game
        """
        self.stop()
        font = ("Arial", 36, "bold")
        self.canvas.create_text(self.screen_width/2,
                                self.screen_height/2,
                                text="You Lose",
                                font=font,
                                fill="red")

    def animate(self):
        """
        Update and render all game's elements. Overrides the animate method
        from the Game class to include collision detection.
        """
        super().animate()

        for enemy in self.enemies:
            if enemy.hits_player():
                self.game_over_lose()
                break

class RandomWalkEnemy(Enemy):
    def __init__(self, game: "TurtleAdventureGame", size: int, color: str):
        super().__init__(game, size, color)
        self.canvas_item = None

    def update(self):
        self.x += random.choice([-5, 5])
        self.y += random.choice([-5, 5])

class ChasingEnemy(Enemy):
    def update(self):
        player = self.game.player
        dx = player.x - self.x
        dy = player.y - self.y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance > 0:
            self.x += dx / distance * 0.5
            self.y += dy / distance * 0.5


class FencingEnemy(Enemy):
    def __init__(self, game: "TurtleAdventureGame", size: int, color: str):
        super().__init__(game, size, color, shape="rectangle")

    def update(self):
        self.x += random.choice([-5, 5])
        self.y += random.choice([-5, 5])

class StealthEnemy(Enemy):
    def __init__(self, game: "TurtleAdventureGame", size: int, color: str):
        super().__init__(game, size, color)
        self.visible = True
        self.visibility_timer = 0
        self.visibility_duration = 100  # How long to stay in one visibility state
        self.visibility_cooldown = 50

    def update(self):
        # StealthEnemy might randomly disappear or reappear
        self.visibility_timer += 1

        if self.visible and self.visibility_timer > self.visibility_duration:
            self.visible = False
            self.visibility_timer = 0 

        elif not self.visible and self.visibility_timer > self.visibility_cooldown:
            self.visible = True
            self.visibility_timer = 0

        if self.visible:
            self.x += random.choice([-1, 0, 1])
            self.y += random.choice([-1, 0, 1])

    def render(self):
        if self.canvas_item:
            self.game.canvas.coords(
                self.canvas_item,
                self.x - self.size, self.y - self.size,
                self.x + self.size, self.y + self.size
            )
            self.game.canvas.itemconfig(
                self.canvas_item,
                state='normal' if self.visible else 'hidden'
            )
