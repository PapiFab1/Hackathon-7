import arcade
import random
from os import path

# Defined constants for the screen size
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 500
SCREEN_TITLE = "Pirate Cove Multiplayer PvP"
GRAVITY = 0.5  # Gravity constant
PLAYER_JUMP_SPEED = 10  # Jumping speed
SPRITE_SCALING = 1.0
DELAY_TIME = 0.3  # Delay in seconds

# Each frame in the sprite sheet is 48x48 pixels
FRAME_WIDTH = 48
FRAME_HEIGHT = 48
NUM_FRAMES_WALK = 6  # Number of frames for walking animations
NUM_FRAMES_ATTACK_1 = 6  # Number of frames for player 1 attack animation
NUM_FRAMES_ATTACK_2 = 6  # Number of frames for player 2 attack animation

DIR = path.dirname(path.abspath(__file__))


class MainMenu(arcade.View):
    """ Main Menu View """

    def __init__(self):
        super().__init__()
        self.texture = arcade.load_texture(path.join(DIR, "main_background.png"))
        self.game_start_color = arcade.color.BLACK  # Default color for "START GAME"
        self.how_to_play_color = arcade.color.BLACK  # Default color for "HOW TO PLAY"
        self.is_transitioning = False

    def on_draw(self):
        arcade.start_render()
        width, height = self.window.get_size()

        # Drawing the background
        arcade.draw_texture_rectangle(
            width // 2,
            height // 2,
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            self.texture
        )

        # Draw text for the game
        arcade.draw_text("Pirate's Cove", 10, 440, arcade.color.BLACK, 40, font_name="Kenney Blocks")
        arcade.draw_text("PLAY - B", 10, 390, self.game_start_color, 30, font_name="Kenney Blocks")
        arcade.draw_text("HOW TO PLAY - I", 10, 340, self.how_to_play_color, 30, font_name="Kenney Blocks")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.B:  # Start the game with "B"
            print("B pressed, starting the game")
            self.game_start_color = arcade.color.RED
            arcade.schedule(self.switch_to_game_board, DELAY_TIME)
        elif key == arcade.key.I:  # How to play
            print("I pressed, switching to How To Play")
            self.how_to_play_color = arcade.color.RED
            arcade.schedule(self.switch_to_how_to_play, DELAY_TIME)
        elif key == arcade.key.ESCAPE:  # Exit the game (if intended)
            print("ESCAPE pressed")
            arcade.schedule(self.switch_main_menu, DELAY_TIME)

    def switch_to_game_board(self, delta_time):
        arcade.unschedule(self.switch_to_game_board)
        game_view = GameBoard()  # Create the game view
        game_view.setup()  # Set up the game elements
        self.window.show_view(game_view)  # Show the game view

    def switch_to_how_to_play(self, delta_time):
        arcade.unschedule(self.switch_to_how_to_play)
        how_to_view = HowTo()  # Create the "How to Play" view
        self.window.show_view(how_to_view)

    def switch_main_menu(self, delta_time):
        """Switch to main menu"""
        arcade.unschedule(self.switch_main_menu)
        main_menu = MainMenu()
        self.window.show_view(main_menu)

class Confetti:
    def __init__(self):
        # Set the position of the confetti randomly at the top of the screen
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(SCREEN_HEIGHT, SCREEN_HEIGHT + 200)
        # Random size for confetti rectangles (width and height)
        self.width = random.randint(5, 10)
        self.height = random.randint(5, 15)
        # Random color
        self.color = random.choice([arcade.color.RED, arcade.color.BLUE, arcade.color.YELLOW, arcade.color.GREEN, arcade.color.PURPLE])
        # Random speed for falling
        self.speed = random.uniform(1, 3)

    def update(self):
        # Move the confetti down
        self.y -= self.speed
        # If confetti goes off-screen, reset to the top
        if self.y < 0:
            self.y = random.randint(SCREEN_HEIGHT, SCREEN_HEIGHT + 200)
            self.x = random.randint(0, SCREEN_WIDTH)
            self.speed = random.uniform(1, 3)

    def draw(self):
        # Draw the confetti as a rectangle or circle
        arcade.draw_rectangle_filled(self.x, self.y, self.width, self.height, self.color)

class GameBoard(arcade.View):
    """ Main Gameplay View """

    def __init__(self):
        super().__init__()
        self.player_list = None
        self.platform_list = None
        self.player1 = None
        self.player2 = None
        self.background = None
        self.is_player1_attacking = False
        self.is_player2_attacking = False
        self.player1_attack_time = 0
        self.player2_attack_time = 0
        self.player1_has_dealt_damage = False  # Track if player 1 has dealt damage
        self.player2_has_dealt_damage = False  # Track if player 2 has dealt damage
        self.player1_health = 5
        self.player2_health = 5
        self.player1_is_dead = False  # Track if player 1 is dead
        self.player2_is_dead = False  # Track if player 2 is dead
        self.player1_death_animation_done = False
        self.player2_death_animation_done = False
        self.heart_texture = arcade.load_texture("heart.png")
        self.attack_damage = 1  # Damage dealt per hit
        self.heart_background_color = (0, 0, 0, 100)
        self.player1_icon = None
        self.player2_icon = None
        self.player_icon_y = 0
        self.game_over = False
        self.winner = None
        self.confetti_list = [Confetti() for _ in range(100)]  # Create 100 confetti particles

    def setup(self):
        """ Set up the main game here """

        # Initialize sprite lists
        self.player_list = arcade.SpriteList()
        self.platform_list = arcade.SpriteList()
        # Create the background image
        self.background = arcade.load_texture("island_map.jpg")

        # Create player 1
        self.player1 = arcade.AnimatedTimeBasedSprite()
        self.player1_walk_frames = []
        self.player1_attack_frames = []
        self.player1_death_frames = []

        # Creating Player Icons
        self.player1_icon = arcade.load_texture(path.join(DIR, "captain_icon.png"), flipped_horizontally=True)
        self.player2_icon = arcade.load_texture(path.join(DIR, "Knightro_icon.png"))

        # Load walking textures for player 1
        for i in range(NUM_FRAMES_WALK):
            texture = arcade.load_texture(
                "Captain_walk.png",  # File path for Captain's walk spritesheet
                x=i * FRAME_WIDTH, y=0, width=FRAME_WIDTH, height=FRAME_HEIGHT
            )
            self.player1_walk_frames.append(arcade.AnimationKeyframe(i, 85, texture))

        # Load attack textures for player 1
        for i in range(NUM_FRAMES_ATTACK_1):
            texture = arcade.load_texture(
                "Captain_attack1.png",  # File path for Captain's attack spritesheet
                x=i * FRAME_WIDTH, y=0, width=FRAME_WIDTH, height=FRAME_HEIGHT
            )
            self.player1_attack_frames.append(arcade.AnimationKeyframe(i, 60, texture))

        # Load death textures for player 1
        for i in range(NUM_FRAMES_ATTACK_1):  # Adjust NUM_FRAMES_ATTACK_1 to the correct number of death frames
            texture = arcade.load_texture("Captain_death.png", x=i * FRAME_WIDTH, y=0, width=FRAME_WIDTH,
                                          height=FRAME_HEIGHT)
            self.player1_death_frames.append(arcade.AnimationKeyframe(i, 100, texture))

        # Set the scaling factor to make the sprite bigger
        self.player1.scale = 2.0  # Adjust this value to change the size

        self.player1.frames = self.player1_walk_frames
        self.player1.texture = self.player1.frames[0].texture
        self.player1.set_hit_box(self.player1.texture.hit_box_points)
        self.player1.center_x = 350
        self.player1.center_y = 200
        self.player_list.append(self.player1)

        # Create player 2
        self.player2 = arcade.AnimatedTimeBasedSprite()
        self.player2_walk_frames = []
        self.player2_attack_frames = []
        self.player2_death_frames = []

        # Load walking textures for player 2
        for i in range(NUM_FRAMES_WALK):
            texture = arcade.load_texture(
                "Knightro_walk_flip.png",  # File path for Pirate's walk spritesheet
                x=i * FRAME_WIDTH, y=0, width=FRAME_WIDTH, height=FRAME_HEIGHT
            )
            self.player2_walk_frames.append(arcade.AnimationKeyframe(i, 85, texture))

        # Load attack textures for player 2
        for i in range(NUM_FRAMES_ATTACK_2):
            texture = arcade.load_texture(
                "Knightro_attack.png",  # File path for Pirate's attack spritesheet
                x=i * FRAME_WIDTH, y=0, width=FRAME_WIDTH, height=FRAME_HEIGHT
            )
            self.player2_attack_frames.append(arcade.AnimationKeyframe(i, 60, texture))

        # Load death textures for player 2
        for i in range(NUM_FRAMES_ATTACK_2):  # Adjust NUM_FRAMES_ATTACK_2 to the correct number of death frames
            texture = arcade.load_texture("Knightro_deathflipped.png", x=i * FRAME_WIDTH, y=0, width=FRAME_WIDTH,
                                          height=FRAME_HEIGHT)
            self.player2_death_frames.append(arcade.AnimationKeyframe(i, 100, texture))

        # Set the scaling factor to make the sprite bigger
        self.player2.scale = 2.0  # Adjust this value to change the size

        self.player2.frames = self.player2_walk_frames
        self.player2.texture = self.player2.frames[0].texture
        self.player2.set_hit_box(self.player2.texture.hit_box_points)
        self.player2.center_x = 650
        self.player2.center_y = 200
        self.player_list.append(self.player2)

        # Create platform
        platform = arcade.Sprite(":resources:images/tiles/grassMid.png", 1)
        platform.width = SCREEN_WIDTH
        platform.center_x = SCREEN_WIDTH // 2
        platform.center_y = 50
        self.platform_list.append(platform)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.background)
        self.player_list.draw()
        self.platform_list.draw()

        # Draw hearts for player 1
        for i in range(self.player1_health):
            arcade.draw_texture_rectangle(110 + i * 45, 440, 55, 45, self.heart_texture)

        # Draw hearts for player 2
        for i in range(self.player2_health):
            arcade.draw_texture_rectangle(890 - i * 45, 440, 55, 45, self.heart_texture)

        # Drawing player icons
        arcade.draw_texture_rectangle(45, 450, 75, 75, self.player1_icon)
        arcade.draw_texture_rectangle(955, 450, 75, 75, self.player2_icon)

        # If the game is over, draw the confetti
        if self.game_over:
            for confetti in self.confetti_list:
                confetti.draw()

        # Game over print out
        if self.game_over:
            arcade.draw_lrtb_rectangle_filled(305, 695, 295, 225, (200, 200, 200, 150))

            # Draw the text over the transparent box
            arcade.draw_text(f"{self.winner} Wins!",
                             SCREEN_WIDTH // 2,
                             SCREEN_HEIGHT // 2,
                             arcade.color.BLACK,
                             25,
                             font_name="Kenney Rocket",
                             anchor_x="center")

            # Draw the "Return to Main Menu" button
            arcade.draw_text("Press ESC to Return to Main Menu", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40, arcade.color.RED, 20, font_name="Kenney Rocket", anchor_x="center")


    def on_update(self, delta_time):
        # If the game is over, update confetti
        if self.game_over:
            for confetti in self.confetti_list:
                confetti.update()

        # Disable further updates and stop gravity/movement if either player is dead
        if self.player1_is_dead and not self.player1_death_animation_done:
            self.player1.change_x = 0
            self.player1.change_y = 0  # Stop gravity
            self.player1.update_animation(delta_time)
            if self.player1.cur_frame_idx == len(self.player1.frames) - 1:
                self.player1_death_animation_done = True  # Freeze on the last frame

        if self.player2_is_dead and not self.player2_death_animation_done:
            self.player2.change_x = 0
            self.player2.change_y = 0  # Stop gravity
            self.player2.update_animation(delta_time)
            if self.player2.cur_frame_idx == len(self.player2.frames) - 1:
                self.player2_death_animation_done = True  # Freeze on the last frame

        # If either player is dead and their animation is done, no further updates
        if self.player1_death_animation_done or self.player2_death_animation_done:
            return

        # Apply gravity if players are alive
        if not self.player1_is_dead:
            self.player1.change_y -= GRAVITY
        if not self.player2_is_dead:
            self.player2.change_y -= GRAVITY

        self.player_list.update()

        # Manage attacks and check for damage
        self.manage_attacks(delta_time)

        # Handle movement for both players if they are alive and not attacking
        if not self.player1_is_dead and self.player1.change_x != 0 and not self.is_player1_attacking:
            self.player1.update_animation(delta_time)

        if not self.player2_is_dead and self.player2.change_x != 0 and not self.is_player2_attacking:
            self.player2.update_animation(delta_time)

        # Handle platform collisions
        for player in [self.player1, self.player2]:
            collisions = arcade.check_for_collision_with_list(player, self.platform_list)
            if collisions:
                player.change_y = 0
                player.bottom = collisions[0].top

        # Limit player1 movement within screen bounds
        if self.player1.left < 0:
            self.player1.left = 0
        if self.player1.right > 1000:
            self.player1.right = 1000

        # Limit player2 movement within screen bounds
        if self.player2.left < 0:
            self.player2.left = 0
        if self.player2.right > 1000:
            self.player2.right = 1000

        # Check if a player dies and set the game_over flag
        if self.player1_health <= 0:
            self.game_over = True
            self.winner = "Player 2"
        elif self.player2_health <= 0:
            self.game_over = True
            self.winner = "Player 1"

    def manage_attacks(self, delta_time):
        """Handle attack logic and damage"""

        # Player 1 attack logic
        if self.is_player1_attacking and not self.player1_is_dead:
            self.player1_attack_time += delta_time
            self.player1.update_animation(delta_time)

            # Check if Player 1 hit Player 2
            if arcade.check_for_collision(self.player1, self.player2) and not self.player1_has_dealt_damage:
                self.player2_health -= self.attack_damage
                self.player2_health = max(0, self.player2_health)
                self.player1_has_dealt_damage = True  # Mark damage as dealt
                print(f"Player 2 hit! Health: {self.player2_health}")

                # If Player 2's health is 0, trigger death animation
                if self.player2_health == 0 and not self.player2_is_dead:
                    self.player2.frames = self.player2_death_frames
                    self.player2.cur_frame_idx = 0  # Start the death animation
                    self.player2_is_dead = True

            # Reset after attack completes
            if self.player1_attack_time > NUM_FRAMES_ATTACK_1 * 0.1:
                self.is_player1_attacking = False
                self.player1_attack_time = 0
                self.player1.frames = self.player1_walk_frames
                self.player1_has_dealt_damage = False  # Reset damage flag

        # Player 2 attack logic
        if self.is_player2_attacking and not self.player2_is_dead:
            self.player2_attack_time += delta_time
            self.player2.update_animation(delta_time)

            # Check if Player 2 hit Player 1
            if arcade.check_for_collision(self.player2, self.player1) and not self.player2_has_dealt_damage:
                self.player1_health -= self.attack_damage
                self.player1_health = max(0, self.player1_health)
                self.player2_has_dealt_damage = True  # Mark damage as dealt
                print(f"Player 1 hit! Health: {self.player1_health}")

                # If Player 1's health is 0, trigger death animation
                if self.player1_health == 0 and not self.player1_is_dead:
                    self.player1.frames = self.player1_death_frames
                    self.player1.cur_frame_idx = 0  # Start the death animation
                    self.player1_is_dead = True

            # Reset after attack completes
            if self.player2_attack_time > NUM_FRAMES_ATTACK_2 * 0.1:
                self.is_player2_attacking = False
                self.player2_attack_time = 0
                self.player2.frames = self.player2_walk_frames
                self.player2_has_dealt_damage = False  # Reset damage flag

    def on_key_press(self, key, modifiers):
        # If game is over, allow return to main menu with ESC
        if self.game_over and key == arcade.key.ESCAPE:
            self.switch_to_main_menu()

        if self.player1_is_dead or self.player2_is_dead:
            return  # Disable input if either player is dead

        # Player 1 movement and attack (WASD + "R")
        if key == arcade.key.D and not self.is_player1_attacking:
            self.player1.change_x = 5
        elif key == arcade.key.A and not self.is_player1_attacking:
            self.player1.change_x = -5
        elif key == arcade.key.W and self.player1.change_y == 0:
            self.player1.change_y = PLAYER_JUMP_SPEED
        elif key == arcade.key.R and not self.is_player1_attacking:
            self.is_player1_attacking = True
            self.player1.frames = self.player1_attack_frames
            self.player1.cur_frame_idx = 0
            self.player1.update_animation(0)

        # Player 2 movement and attack (Arrow keys + "/")
        if key == arcade.key.RIGHT and not self.is_player2_attacking:
            self.player2.change_x = 5
        elif key == arcade.key.LEFT and not self.is_player2_attacking:
            self.player2.change_x = -5
        elif key == arcade.key.UP and self.player2.change_y == 0:
            self.player2.change_y = PLAYER_JUMP_SPEED
        elif key == arcade.key.SLASH and not self.is_player2_attacking:
            self.is_player2_attacking = True
            self.player2.frames = self.player2_attack_frames
            self.player2.cur_frame_idx = 0
            self.player2.update_animation(0)

    def switch_to_main_menu(self):
        """ Switch to the Main Menu view """
        main_menu = MainMenu()
        self.window.show_view(main_menu)

    def on_key_release(self, key, modifiers):
        # Player 2 key release
        if key in [arcade.key.RIGHT, arcade.key.LEFT]:
            self.player2.change_x = 0

        # Player 1 key release
        if key in [arcade.key.D, arcade.key.A]:
            self.player1.change_x = 0


class HowTo(arcade.View):
    def __init__(self):
        super().__init__()
        # Init the images used
        self.texture = arcade.load_texture(path.join(DIR, "how_to_pic.png"))
        self.red_esc = arcade.load_texture(path.join(DIR, "esc_red.png"))
        self.black_esc = arcade.load_texture(path.join(DIR, "esc_black.png"))
        self.cur_foreground = self.black_esc

        self.down_arrow = arcade.load_texture(path.join(DIR, "down_arrow.png"))

        self.is_transitioning = False  # Flag to check if already transitioning
        # Text color
        self.escape_color = arcade.color.BLACK

    def on_show_view(self):
        """ Reset all necessary variables and states """
        pass

    def on_draw(self):
        arcade.start_render()  # clear prev screen to start drawing

        # Get window dimensions
        width, height = self.window.get_size()

        # Scale the background to window size
        scaled_width = SCREEN_WIDTH
        scaled_height = SCREEN_HEIGHT

        # Drawing the background
        arcade.draw_texture_rectangle(
            width // 2,
            height // 2,
            scaled_width,
            scaled_height,
            self.texture
        )

        escape_coord_x = 25
        escape_coord_y = 485
        # Drawing escape button
        arcade.draw_texture_rectangle(
            escape_coord_x,
            escape_coord_y,
            50,
            25,  # Desired height for the image on top
            self.cur_foreground  # The foreground texture
        )

        arcade.draw_texture_rectangle(
            207, 347,
            17, 10,
            self.down_arrow
        )

        # Drawing text 'escape' next to button
        esc_txt_x = escape_coord_x + 25
        arcade.draw_text("ESCAPE",
                         esc_txt_x,
                         479,
                         self.escape_color,
                         15,
                         font_name="Kenney Rocket")

        # Introduction to game
        arcade.draw_text(
            "Ahoy!! This is Pirate's Cove. Where the strongest pirate "
            "is the greatest pirate of them all!\nUse whatever is at your disposal and fight other "
            "pirates to protect your treasure and pride.",
            SCREEN_WIDTH // 2,  # Center the x-coordinate based on the screen width
            400,  # y-coordinate
            arcade.color.BLACK,  # Text color
            13,  # Font size
            width=800,  # Width of the text box
            multiline=True,  # Enable multiline text
            align="center",  # Align text to center
            anchor_x="center",  # Set anchor point for x to the center
            font_name="Kenney Rocket"
        )

        # Draw the filled rectangles for Player 1 and Player 2 control boxes
        arcade.draw_lrtb_rectangle_filled(250, 450, 300, 200, arcade.color.LIGHT_GRAY)  # Player 1
        arcade.draw_lrtb_rectangle_filled(550, 750, 300, 200, arcade.color.LIGHT_GRAY)  # Player 2

        # Draw the outlines around the control boxes
        arcade.draw_lrtb_rectangle_outline(250, 450, 300, 200, arcade.color.BLACK, 2)  # Player 1 outline
        arcade.draw_lrtb_rectangle_outline(550, 750, 300, 200, arcade.color.BLACK, 2)  # Player 2 outline

        text_p_one_x = 520
        text_p_one_y = 280

        # Player 1 controls
        arcade.draw_text("Player 1\n"
                         "Left:\t\tA \n"
                         "Right:\t\tD\n"
                         "Up:\t\t\tW\n"
                         "Attack:\t\tR",
                         text_p_one_x, text_p_one_y,
                         arcade.color.BLACK,
                         10, width=500,
                         multiline=True, anchor_x="center",
                         font_name="Kenney Rocket"
                         )

        text_p_two_x = 820
        text_p_two_y = 280
        # Player 2 controls
        arcade.draw_text("Player 2\n"
                         "Left:\t\t< \n"
                         "Right:\t\t>\n"
                         "Up:\t\t\t^\n"
                         "Attack:\t\t/\n",
                         text_p_two_x, text_p_two_y,
                         arcade.color.BLACK,
                         10, width=500,
                         multiline=True, anchor_x="center",
                         font_name="Kenney Rocket"
                         )

        # Player 1 controls

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:  # Go back to main menu
            self.cur_foreground = self.red_esc
            self.escape_color = arcade.color.RED
            self.is_transitioning = True  # Set flag to prevent multiple transitions
            arcade.schedule(self.switch_main_menu, DELAY_TIME)

    def switch_main_menu(self, delta_time):
        """ Switch to the Main Menu view after a delay """
        arcade.unschedule(self.switch_main_menu)  # Stop further scheduling of this function
        self.window.show_view(MainMenu())


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    main_menu = MainMenu()
    window.show_view(main_menu)
    arcade.run()


if __name__ == "__main__":
    main()
