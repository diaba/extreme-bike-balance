# Bike Balance Game: Development Guide

Follow these instructions to program a physics-based bike balancing game.

---

## 1. Project Setup & Assets
* **Images:** * `background.png`: A wide image for the environment.
    * `bike.png`: The player character (use a transparent PNG).
* **Coordinate System:** * Keep the bike centered on the $x$-axis.
    * (Optional) Scroll the background to simulate forward motion.

## 2. Physics Variables
Initialize these variables at the start of your script:

| Variable | Purpose |
| :--- | :--- |
| `angle` | The current rotation of the bike (starts at 0). |
| `angular_velocity` | The speed at which the bike is tilting. |
| `gravity_pull` | A constant that pulls the bike down faster as the angle increases. |
| `lean_speed` | The power of the player's input (W/S keys). |

---

## 3. The Core Game Logic
To create realistic balancing, run the following logic inside your main game loop:

### Gravity Calculation
Gravity is non-linear; the further the bike tilts, the harder it falls.
$$angular\_velocity += angle \times gravity\_strength$$

### Input Handling
* **Press W:** Lean Back (Decrease `angular_velocity`).
* **Press S:** Lean Forward (Increase `angular_velocity`).

### Rotation Update
Apply the calculated velocity to the current angle:
$$angle += angular\_velocity$$

### Win/Loss Condition
* **Collision:** If `angle` > 90° or `angle` < -90°, trigger a **Game Over**.

---

## 4. Score Tracking
* **Current Score:** Increment a counter for every second the player remains upright.
* **High Score:** * At Game Over, check if `current_score` > `high_score`.
    * Save the new `high_score` to local storage or a `.txt` file.