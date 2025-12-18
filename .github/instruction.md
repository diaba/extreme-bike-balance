# AI Developer Instructions: Extreme Bike Balance Engine

You are a Python Game Development expert. Use these instructions to maintain, debug, or extend the provided Pygame source code.

## 1. Core Architecture

The game follows a **State-Driven Object-Oriented** pattern.

- **States**: `MENU`, `PLAYING`, `GAMEOVER`.
- **Primary Classes**:
  - `Game`: Controls the main loop, state transitions, and UI.
  - `Bike`: Encapsulates physics, visual scaling, and nitro fuel.
  - `Background`: Handles infinite parallax scrolling.

## 2. Physics & Balance Logic

The balance mechanic uses an angular velocity formula influenced by gravity and user input:

- **Gravity Scaling**: $G_{current} = G_{base} + (Score / 45000)$.
- **Angular Velocity**: $\omega_{t+1} = \omega_t + (\theta \cdot G) + Wind$.
- **Stabilization**: Boosting (holding SPACE) reduces the gravity multiplier by 40%, making the bike easier to balance at high speeds.

## 3. Bike Configuration Data

Bikes are defined in a dictionary `BIKE_CONFIGS`. When adding new bikes, follow this schema:

- `grav`: Base falling speed (Stability).
- `lean`: How responsive the W/S keys are (Handling).
- `speed`: Multiplier for score and background scroll.
- `img`: Filename for the sprite.

## 4. UI & High Score System

- **Persistence**: High scores are stored in `record.pkl` using the `pickle` module.
- **Scaling**: All visual scores are displayed as `Score // 10` to represent meters.
- **HUD**: Includes a real-time "Best Score" tracker that updates the moment the player surpasses the previous record.

## 5. Asset Requirements

The engine expects the following assets in the root directory:

1. `bg.png`: Infinite scroll background (Min 800px width).
2. `bike1.png`, `bike2.png`, `bike3.png`: Transparent PNG sprites.
3. `record.pkl`: Automatically generated on first wipeout.

## 6. Extension Guidelines

- **To add Obstacles**: Create an `Obstacle` class and a list in `Game`. Check for collisions using `bike.rect.colliderect()`.
- **To add Visuals**: Insert particle emission calls in the `PLAYING` state loop.
- **To add Levels**: Create a `LevelManager` that swaps `bg.png` based on `score` milestones.
