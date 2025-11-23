from ursina import *
from random import uniform, choice
import sys

class Airplane(Entity):
    def __init__(self):
        super().__init__(
            model='cube',
            color=color.blue,
            scale=(1, 0.3, 1.5),
            position=(0, 0, 0),
            collider='box'
        )
        # Add wings
        self.left_wing = Entity(
            model='cube',
            color=color.azure,
            scale=(2, 0.1, 0.5),
            position=(-1.5, 0, 0),
            parent=self
        )
        self.right_wing = Entity(
            model='cube',
            color=color.azure,
            scale=(2, 0.1, 0.5),
            position=(1.5, 0, 0),
            parent=self
        )
        # Add tail
        self.tail = Entity(
            model='cube',
            color=color.red,
            scale=(0.3, 0.8, 0.3),
            position=(0, 0.3, -0.7),
            parent=self
        )
        
        self.speed = 5
        self.move_range = 8
        
    def update(self):
        # Horizontal movement
        if held_keys['left arrow'] or held_keys['a']:
            self.x -= self.speed * time.dt
        if held_keys['right arrow'] or held_keys['d']:
            self.x += self.speed * time.dt
        
        # Vertical movement
        if held_keys['up arrow'] or held_keys['w']:
            self.y += self.speed * time.dt
        if held_keys['down arrow'] or held_keys['s']:
            self.y -= self.speed * time.dt
        
        # Keep airplane within bounds
        self.x = clamp(self.x, -self.move_range, self.move_range)
        self.y = clamp(self.y, -4, 4)
        
        # Add slight tilt based on movement
        if held_keys['left arrow'] or held_keys['a']:
            self.rotation_z = lerp(self.rotation_z, 15, time.dt * 5)
        elif held_keys['right arrow'] or held_keys['d']:
            self.rotation_z = lerp(self.rotation_z, -15, time.dt * 5)
        else:
            self.rotation_z = lerp(self.rotation_z, 0, time.dt * 5)


class Coin(Entity):
    def __init__(self, position):
        super().__init__(
            model='sphere',
            color=color.gold,
            scale=1.2,
            position=position,
            collider='sphere'
        )
        self.speed = 10
        
    def update(self):
        self.z -= self.speed * time.dt
        self.rotation_y += 100 * time.dt
        
        # Remove if too far behind
        if self.z < -10:
            destroy(self)


class Obstacle(Entity):
    def __init__(self, position, obstacle_type='cube'):
        if obstacle_type == 'cube':
            model_type = 'cube'
            scale_val = (1.5, 3, 1.5)
            color_val = color.red
        elif obstacle_type == 'sphere':
            model_type = 'sphere'
            scale_val = 2.5
            color_val = color.orange
        else:  # pyramid
            model_type = 'cube'
            scale_val = (2, 2, 2)
            color_val = color.violet
            
        super().__init__(
            model=model_type,
            color=color_val,
            scale=scale_val,
            position=position,
            collider='box'
        )
        self.speed = 10
        
    def update(self):
        self.z -= self.speed * time.dt
        self.rotation_y += 30 * time.dt
        
        # Remove if too far behind
        if self.z < -10:
            destroy(self)


class Ground(Entity):
    def __init__(self, z_pos):
        super().__init__(
            model='plane',
            color=color.green,
            scale=(50, 1, 10),
            position=(0, -6, z_pos),
            rotation_x=0
        )
        self.speed = 10
        
    def update(self):
        self.z -= self.speed * time.dt
        
        # Reset position when too far behind
        if self.z < -20:
            self.z += 40


class Game:
    def __init__(self):
        self.score = 0
        self.distance = 0
        self.game_over = False
        self.spawn_timer = 0
        self.spawn_interval = 1.5
        
        # Create player
        self.player = Airplane()
        
        # Create ground segments for endless effect
        self.grounds = [Ground(i * 10) for i in range(5)]
        
        # Simple UI
        self.score_text = Text(
            text=f'Score: {self.score}',
            position=(-0.85, 0.45),
            scale=2,
            color=color.yellow
        )
        
        self.distance_text = Text(
            text=f'Distance: {int(self.distance)}m',
            position=(-0.85, 0.40),
            scale=1.5,
            color=color.white
        )
        
        self.game_over_text = Text(
            text='',
            position=(0, 0.1),
            scale=3,
            color=color.red,
            origin=(0, 0),
            visible=False
        )
        
        self.restart_text = Text(
            text='',
            position=(0, -0.05),
            scale=1.5,
            color=color.white,
            origin=(0, 0),
            visible=False
        )
        
        # Lists to track entities
        self.coins = []
        self.obstacles = []
        
    def update(self):
        if self.game_over:
            return
            
        # Update distance
        self.distance += 10 * time.dt
        self.distance_text.text = f'Distance: {int(self.distance)}m'
        
        # Spawn coins and obstacles
        self.spawn_timer += time.dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self.spawn_objects()
        
        # Check coin collection
        for coin in self.coins[:]:
            if coin.intersects(self.player).hit:
                self.score += 10
                self.score_text.text = f'Score: {self.score}'
                destroy(coin)
                self.coins.remove(coin)
        
        # Check obstacle collision
        for obstacle in self.obstacles[:]:
            if obstacle.intersects(self.player).hit:
                self.end_game()
                break
    
    def spawn_objects(self):
        # Random spawn position
        x_pos = uniform(-6, 6)
        y_pos = uniform(-2, 3)
        z_pos = 25
        
        # 60% chance to spawn coin, 40% chance to spawn obstacle
        if uniform(0, 1) < 0.6:
            coin = Coin(position=(x_pos, y_pos, z_pos))
            self.coins.append(coin)
        else:
            obstacle_type = choice(['cube', 'sphere', 'pyramid'])
            obstacle = Obstacle(position=(x_pos, y_pos, z_pos), obstacle_type=obstacle_type)
            self.obstacles.append(obstacle)
    
    def end_game(self):
        self.game_over = True
        self.game_over_text.text = f'GAME OVER!\nFinal Score: {self.score}\nDistance: {int(self.distance)}m'
        self.game_over_text.visible = True
        self.restart_text.text = 'Press R to Restart or ESC to Exit'
        self.restart_text.visible = True
        
        # Stop all moving objects
        for coin in self.coins:
            coin.speed = 0
        for obstacle in self.obstacles:
            obstacle.speed = 0
        for ground in self.grounds:
            ground.speed = 0
    
    def restart(self):
        # Clean up old entities
        for coin in self.coins[:]:
            destroy(coin)
        for obstacle in self.obstacles[:]:
            destroy(obstacle)
        
        self.coins.clear()
        self.obstacles.clear()
        
        # Reset game state
        self.score = 0
        self.distance = 0
        self.game_over = False
        self.spawn_timer = 0
        
        # Reset player position
        self.player.position = (0, 0, 0)
        
        # Reset ground speeds
        for ground in self.grounds:
            ground.speed = 10
        
        # Reset UI
        self.score_text.text = f'Score: {self.score}'
        self.distance_text.text = f'Distance: {int(self.distance)}m'
        self.game_over_text.visible = False
        self.restart_text.visible = False


# Initialize Ursina
app = Ursina()

# Setup camera
camera.position = (0, 3, -15)
camera.rotation_x = 10

# Create sky
Sky()

# Create game instance
game = Game()

# Global update function that Ursina calls every frame
def update():
    game.update()

# Input handling
def input(key):
    if key == 'escape':
        sys.exit()
    
    if key == 'r' and game.game_over:
        game.restart()

# Add instructions
instructions = Text(
    text='Use Arrow Keys or WASD to move\nCollect coins, avoid obstacles!\nPress ESC to exit',
    position=(0, 0.3),
    scale=1.5,
    color=color.white,
    origin=(0, 0)
)

def hide_instructions():
    destroy(instructions)

# Hide instructions after 5 seconds
invoke(hide_instructions, delay=5)

# Run the game
app.run()