# 2D Space Neon Shooter - Exhaustive Technical Documentation

This document provides a comprehensive breakdown of the internal mechanics, architecture, rendering pipeline, and algorithms powering the 2D Space Neon Shooter prototype.

---

## 1. Technology Stack & Requirements

The project leverages Python 3.12 and relies on a focused set of libraries to handle hardware-accelerated rendering and window management.

### Dependencies
- **pygame (v2.6.1)**: Used exclusively for window creation, OpenGL context initialization, input capturing (keyboard and mouse), and audio mixing. It acts as the bridge between the OS and the game logic.
- **PyOpenGL & PyOpenGL_accelerate (v3.1.10)**: The official Python bindings for OpenGL. The game uses the Modern OpenGL API (Core Profile 3.3) instead of deprecated fixed-function pipelines (like `glBegin`/`glEnd`), allowing direct manipulation of Vertex Buffer Objects (VBOs) and custom GLSL shaders.
- **numpy (v2.4.4)**: The backbone for all mathematical operations in the game. It is used to generate 4x4 transformation matrices for the rendering pipeline and to synthesize audio waveforms dynamically.

---

## 2. Core Architecture

The game is separated into highly modular components, prioritizing separation of concerns between game logic, physics, rendering, and audio.

### File Structure
- **`main.py`**: The application entry point.
- **`game.py`**: The core logic orchestrator.
- **`entity.py`**: The physics and object definition module.
- **`ui.py`**: The text-to-texture rendering module.
- **`shader.py`**: The OpenGL shader compilation module.
- **`sound.py`**: The procedural audio synthesis module.
- **`shaders/`**: Directory containing raw GLSL source code.

---

## 3. Game Logic & Mechanics

### 3.1 Game Loop (`main.py`)
The game runs on a fixed-timestep loop using `pygame.time.Clock().tick(60)`. This caps the game at 60 Frames Per Second (FPS) and provides a delta-time (`dt`) value in seconds. Delta-time is passed down to all update functions, ensuring that physics and movement are frame-rate independent (e.g., an object moving at 100 pixels/sec will move 100 pixels regardless of whether the game is running at 30 FPS or 144 FPS).

### 3.2 State Machine (`game.py`)
The `Game` class manages three primary states using the `GameState` enum:
1. **`MENU`**: Renders the title screen. Pauses all entity updates.
2. **`PLAYING`**: Processes physics, collisions, enemy spawning, and user input.
3. **`GAME_OVER`**: Freezes game physics but continues to render the screen behind the Game Over text, waiting for the user to restart.

### 3.3 Physics & Movement (`entity.py`)
All physical objects inherit from the base `Entity` class.
- **Integration**: Position is updated using simple Euler integration: 
  `self.x += self.vx * dt` and `self.y += self.vy * dt`.
- **Absolute Vector Thrust (Player)**: When WASD is pressed, a directional vector `(dx, dy)` is calculated. If moving diagonally, `math.hypot` is used to normalize the vector (divide `dx` and `dy` by the length) so diagonal movement isn't faster than cardinal movement. This normalized vector is multiplied by acceleration.
- **Friction**: When no keys are pressed, friction subtracts from the player's total speed (calculated via `math.hypot(vx, vy)`), and the individual `vx/vy` components are scaled down proportionally.
- **Screen Wrapping**: The game operates in a toroidal space. If an object's X or Y coordinates exceed the window bounds (plus a 30px margin to hide the visual snapping), they are teleported to the opposite side of the screen.

### 3.4 Aiming & Input
- **Mouse Aiming**: The player's rotation angle is calculated dynamically using `math.atan2(mouse_y - player_y, mouse_x - player_x)`. 
- **Shooting**: Projectiles are spawned at the "tip" of the player's triangle by calculating `(player.x + cos(angle)*15, player.y + sin(angle)*15)`. The projectile inherits the player's angle and applies a high velocity vector in that direction.

### 3.5 Collision Detection
The game uses simple, highly performant Circle-based collision detection. Every entity has an active `radius`. A collision occurs if the Euclidean distance between two entities (`math.hypot(x2-x1, y2-y1)`) is strictly less than the sum of their radii (`radius1 + radius2`).

---

## 4. Modern OpenGL Rendering Pipeline

This game strictly avoids immediate mode (`glBegin`) to ensure high performance and adherence to modern graphics programming standards.

### 4.1 Vertex Buffer Objects (VBO) & Vertex Array Objects (VAO)
When an `Entity` is instantiated, it defines a raw array of 2D vertices (its geometric shape). 
1. `glGenVertexArrays` and `glGenBuffers` allocate memory on the GPU.
2. The python `list` of vertices is cast to a 32-bit float `numpy.array`.
3. `glBufferData` uploads this contiguous memory block directly into the GPU's VRAM.
4. `glVertexAttribPointer` tells the GPU how to interpret the byte layout (groups of 2 floats representing X and Y).

### 4.2 Matrix Mathematics
OpenGL requires vertices to be multiplied by Transformation Matrices to position them correctly on the screen.
- **Translation Matrix**: Moves the object to `(self.x, self.y)`.
- **Rotation Matrix**: Rotates the object by `self.angle`.
- **Model Matrix Calculation**: `Model = Translation Matrix @ Rotation Matrix`. This specific order (`T * R`) guarantees that the object rotates around its local center before being translated into world space. 
- **Orthographic Projection**: The `ortho_matrix` transforms 2D world coordinates (e.g., `X: 0 to 1280`, `Y: 0 to 720`) into Normalized Device Coordinates (NDC) ranging from `-1.0 to 1.0`, which OpenGL requires to rasterize pixels.

### 4.3 Shader Programs (`shader.py`)
- **Vertex Shader (`neon.vert`)**: Multiplies the incoming vertex by the `projection` and `model` matrices.
- **Fragment Shader (`neon.frag`)**: Determines the pixel color. It takes a `neonColor` uniform and an `intensity` float. 
- **Two-Pass Rendering**: Entities are rendered twice per frame. 
  1. `glDrawArrays(GL_TRIANGLE_FAN)`: Renders the solid interior polygon using a dark, desaturated color (`fill_color`).
  2. `glDrawArrays(GL_LINE_LOOP)`: Renders the glowing wireframe border using a high-intensity neon color.
- **Additive Blending**: `glBlendFunc(GL_SRC_ALPHA, GL_ONE)` instructs OpenGL to add overlapping colors together rather than overwriting them, naturally producing a bright "bloom" or neon glow effect when lines intersect.

---

## 5. UI and Text Rendering (`ui.py`)

Rendering text natively in OpenGL is incredibly complex (requiring parsing `.ttf` font glyphs into texture atlases and mapping UV coordinates). The `TextRenderer` uses a clever hybrid approach:
1. `pygame.font.SysFont` renders the requested text string into a hidden, 2D pixel Surface.
2. `pygame.image.tostring` extracts the raw RGBA byte data from that surface.
3. `glTexImage2D` dynamically uploads that byte data into the GPU as a 2D OpenGL Texture.
4. A square quad (composed of 4 vertices via `GL_TRIANGLE_FAN`) is drawn, and a specific UI shader (`text.vert`, `text.frag`) maps the texture onto the quad, discarding empty pixels and applying a dynamic `textColor` tint.

---

## 6. Procedural Audio Synthesis (`sound.py`)

Instead of loading `.wav` or `.mp3` files from the hard drive, the `SoundManager` generates sound mathematically during initialization.

### Audio Buffer Generation
1. **Sample Rate**: Audio is calculated at `44,100` samples per second (standard CD quality).
2. **Shooting Sound (Square Wave)**:
   - An array of time steps is generated via `numpy.linspace`.
   - `numpy.sin` generates a sine wave at 880 Hz.
   - `numpy.sign` converts the smooth sine wave into a harsh Square Wave, giving it a distinct retro "pew" sound.
3. **Explosion Sound (White Noise)**:
   - `numpy.random.uniform` generates thousands of random values between -1.0 and 1.0, creating pure static (white noise).
4. **Envelope (Fade Out)**:
   - A linear fade array (from 1.0 to 0.0) is multiplied against the raw wave to prevent the sound from "clicking" instantly when it finishes.
5. **Pygame Integration**: The floating-point arrays are scaled to 16-bit integers, duplicated into stereo (two columns), and passed into `pygame.sndarray.make_sound()`, creating fully playable in-memory audio objects.
