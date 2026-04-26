# 2D Space Neon Shooter

A fast-paced, momentum-based 2D arcade shooter built with Python, Pygame, and Modern OpenGL (Core Profile). Featuring a retro Synthwave/Neon aesthetic, programmatic audio synthesis, and custom GLSL shaders.

## Game Mechanics
- **Momentum Physics**: The player ship features absolute-directional movement with acceleration and friction. 
- **Screen Wrapping**: Objects that go off the screen seamlessly wrap around to the other side.
- **Dynamic Combat**: Survive endless waves of enemies. Enemies continuously spawn at an increasing rate as your score goes up.
- **Invincibility Frames**: Taking damage grants a brief window of invincibility, indicated by a blinking ship. You start with 3 lives.
- **Procedural Sound**: Sound effects (lasers and explosions) are mathematically synthesized on-the-fly using numpy and Pygame's sound array buffers—no external audio files required!

## Controls
- **W, A, S, D**: Move (Up, Left, Down, Right)
- **Mouse**: Aim
- **Left Click** or **Spacebar**: Shoot
- **Spacebar**: Start Game / Restart Game

## Architecture
The game follows an object-oriented architecture leveraging Pygame for context/input management and PyOpenGL for hardware-accelerated rendering.
- `main.py`: Entry point, handles Pygame window creation, OpenGL context configuration, and the main game loop.
- `game.py`: Central game state manager (`MENU`, `PLAYING`, `GAME_OVER`), orchestrating input handling, physics updates, enemy spawning, and collision detection.
- `entity.py`: Base entity system and derived classes (`Player`, `Projectile`, `Enemy`, `Particle`). Handles 2D affine transformations (Translation/Rotation matrices) and OpenGL Vertex Buffer Object (VBO) management.
- `shader.py`: Wrapper class to compile, link, and utilize custom GLSL vertex and fragment shaders.
- `sound.py`: Audio synthesis engine that generates retro square wave and white noise buffers to produce dynamic SFX.
- `ui.py`: Renders Pygame TrueType fonts onto off-screen surfaces, uploads them as OpenGL textures, and renders them to the screen using a dedicated text shader.

## How to Run

### 1. Prerequisites
Ensure you have Python 3.x installed on your system. 

### 2. Setup Virtual Environment
Run the included PowerShell script to automatically create a virtual environment and install dependencies:
```powershell
.\setup.ps1
```
Dependencies include: `pygame`, `PyOpenGL`, `PyOpenGL_accelerate`, and `numpy`.

### 3. Play the Game
Activate your virtual environment and run the main script:
```powershell
.\.venv\Scripts\python main.py
```
