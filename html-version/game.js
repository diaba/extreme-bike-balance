const BIKES = {
  1: {
    name: "COBRA",
    img: "./assets/bike1.png",
    grav: 1.2,
    lean: 0.5,
    speed: 2.0,
    color: "#00ff88",
  },
  2: {
    name: "FATBOY",
    img: "./assets/bike2.png",
    grav: 0.7,
    lean: 0.2,
    speed: 1.1,
    color: "#ff8800",
  },
  3: {
    name: "V-RAPTOR",
    img: "./assets/bike3.png",
    grav: 1.5,
    lean: 0.7,
    speed: 2.8,
    color: "#ff0044",
  },
};

class Game {
  constructor() {
    this.canvas = document.getElementById("gameCanvas");
    this.ctx = this.canvas.getContext("2d");
    this.musicElement = document.getElementById("game-music");
    this.resize();
    this.score = 0;
    this.keys = {};
    this.particles = [];
    this.shake = 0;
    this.nitro = 100;
    this.levelIntensity = 0;
    this.audioCtx = null;
    this.isMusicEnabled = false;

    // Environmental Wind
    this.windForce = 0;
    this.targetWind = 0;
    this.windStreaks = [];
    for (let i = 0; i < 15; i++) this.resetWindStreak(true);

    window.addEventListener("resize", () => this.resize());
    document
      .getElementById("music-toggle")
      .addEventListener("click", () => this.toggleMusic());

    window.addEventListener("keydown", (e) => {
      this.keys[e.key] = true;
      if (!this.audioCtx) this.initAudio();
    });
    window.addEventListener("keyup", (e) => (this.keys[e.key] = false));
    this.setupMenu();
  }

  handleAudioUpload(event) {
    const file = event.target.files[0];
    if (file) {
      this.musicElement.src = URL.createObjectURL(file);
      this.musicElement.load();
    }
  }

  initAudio() {
    if (this.audioCtx) return;
    this.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    this.engineOsc = this.audioCtx.createOscillator();
    this.engineGain = this.audioCtx.createGain();
    this.engineOsc.type = "sawtooth";
    this.engineOsc.connect(this.engineGain);
    this.engineGain.connect(this.audioCtx.destination);
    this.engineGain.gain.value = this.isMusicEnabled ? 0.05 : 0;
    this.engineOsc.start();
  }

  toggleMusic() {
    this.isMusicEnabled = !this.isMusicEnabled;
    const btn = document.getElementById("music-toggle");
    btn.innerText = this.isMusicEnabled ? "🎵 MUSIC: ON" : "🎵 MUSIC: OFF";
    if (this.isMusicEnabled) {
      if (this.musicElement.src) this.musicElement.play();
    } else {
      this.musicElement.pause();
    }
    if (this.engineGain) {
      const targetVol = this.isMusicEnabled ? 0.05 : 0;
      this.engineGain.gain.setTargetAtTime(
        targetVol,
        this.audioCtx.currentTime,
        0.1
      );
    }
  }

  updateAudio(isBoosting) {
    if (!this.engineOsc || !this.isMusicEnabled) return;
    let baseFreq = 50 + this.score / 500 + this.levelIntensity * 10;
    if (isBoosting) baseFreq *= 1.4;
    this.engineOsc.frequency.setTargetAtTime(
      baseFreq,
      this.audioCtx.currentTime,
      0.1
    );
  }

  resetWindStreak(randomX = false) {
    this.windStreaks.push({
      x: randomX
        ? Math.random() * this.canvas.width
        : this.targetWind > 0
        ? -200
        : this.canvas.width + 200,
      y: Math.random() * this.canvas.height,
      len: 50 + Math.random() * 100,
      opacity: 0.1 + Math.random() * 0.2,
    });
  }

  resize() {
    this.canvas.width = window.innerWidth;
    this.canvas.height = window.innerHeight;
  }

  setupMenu() {
    const list = document.getElementById("bike-selection");
    if (!list) return;
    list.innerHTML = "";
    Object.entries(BIKES).forEach(([id, b]) => {
      list.innerHTML += `<div class="col-md-4" onclick="engine.start('${id}')"><div class="bike-card p-3 rounded-4 shadow"><img src="${b.img}" style="height:100px; object-fit:contain" class="mb-2"><h4 class="fw-bold" style="color:${b.color}">${b.name}</h4></div></div>`;
    });
  }

  start(id) {
    this.config = BIKES[id];
    this.bike = {
      angle: 0,
      vel: 0,
      y: this.canvas.height / 2 + 80,
      img: new Image(),
      suspension: 0,
    };
    this.bike.img.crossOrigin = "anonymous";
    this.bike.img.src = this.config.img;
    this.state = "PLAYING";
    this.score = 0;
    this.nitro = 100;
    document.getElementById("ui-layer").classList.add("d-none");
    document.getElementById("hud").classList.remove("d-none");
    if (this.isMusicEnabled && this.musicElement.src) this.musicElement.play();
    this.loop();
  }

  loop() {
    if (this.state !== "PLAYING") return;

    // LEVEL DIFFICULTY BASED ON VELOCITY
    this.levelIntensity = Math.abs(this.bike.vel) * 20;

    // Wind Logic scaled by Velocity
    if (Math.random() < 0.005 + this.levelIntensity / 100) {
      this.targetWind =
        (Math.random() - 0.5) * (0.035 + this.levelIntensity / 50);
    }
    this.windForce += (this.targetWind - this.windForce) * 0.02;

    const isBoosting = this.keys[" "] && this.nitro > 0;
    let control = 0;
    if (this.keys["w"] || this.keys["W"]) control = -this.config.lean;
    if (this.keys["s"] || this.keys["S"]) control = this.config.lean;

    this.bike.vel +=
      control + this.bike.angle * (0.0055 * this.config.grav) + this.windForce;

    if (isBoosting) {
      this.bike.vel *= 0.85;
      this.nitro -= 0.6;
      this.shake = 4 + this.levelIntensity;
      this.particles.push({
        x: this.canvas.width / 2 - 140,
        y: this.bike.y + 40,
        vx: -8 - this.levelIntensity,
        vy: Math.random() * 4 - 2,
        life: 1,
        color: this.config.color,
      });
    } else if (this.nitro < 100) {
      this.nitro += 0.15;
    }

    this.bike.vel *= 0.95;
    this.bike.angle += this.bike.vel;
    this.bike.suspension =
      Math.sin(Date.now() / 150) * (3 + this.levelIntensity);
    this.score += this.config.speed + this.levelIntensity;

    if (this.levelIntensity > 0.5)
      this.shake = Math.max(this.shake, this.levelIntensity * 6);

    this.updateAudio(isBoosting);
    this.draw();
    if (Math.abs(this.bike.angle) > 1.55) this.endGame();
    else requestAnimationFrame(() => this.loop());
  }

  draw() {
    const { ctx, canvas, bike } = this;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.save();
    if (this.shake > 0) {
      ctx.translate(
        (Math.random() - 0.5) * this.shake,
        (Math.random() - 0.5) * this.shake
      );
      this.shake *= 0.9;
    }

    // Visual Wind & Parallax
    ctx.strokeStyle = "white";
    this.windStreaks.forEach((s, i) => {
      ctx.globalAlpha = s.opacity;
      ctx.beginPath();
      ctx.moveTo(s.x, s.y);
      ctx.lineTo(s.x + s.len, s.y);
      ctx.stroke();
      s.x += this.windForce * 500 - (6 + this.levelIntensity * 2);
      if (s.x > canvas.width + 200 || s.x < -300) {
        this.windStreaks.splice(i, 1);
        this.resetWindStreak();
      }
    });

    // Big Bike Rendering
    ctx.save();
    ctx.translate(canvas.width / 2, bike.y + bike.suspension);
    ctx.rotate(this.bike.angle);
    ctx.shadowBlur = 40 + this.levelIntensity * 10;
    ctx.shadowColor = this.config.color;
    if (this.bike.img.complete)
      ctx.drawImage(this.bike.img, -160, -90, 320, 180);
    ctx.restore();
    ctx.restore();

    document.getElementById("dist-ui").innerText = `${Math.floor(
      this.score / 10
    )}m`;
    document.getElementById("nitro-fill").style.width = `${this.nitro}%`;
  }

  endGame() {
    this.state = "GAMEOVER";
    this.musicElement.pause();
    if (this.engineGain)
      this.engineGain.gain.setTargetAtTime(0, this.audioCtx.currentTime, 0.1);
    document.getElementById("ui-layer").classList.remove("d-none");
    document.getElementById("menu-screen").classList.add("d-none");
    document.getElementById("gameover-screen").classList.remove("d-none");
    document.getElementById("final-stats").innerText = `DISTANCE: ${Math.floor(
      this.score / 10
    )}m`;
  }
}

const engine = new Game();
