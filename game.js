"use strict";

const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
const gameWrap = document.getElementById("gameWrap");
const loadingMessage = document.getElementById("loadingMessage");
const soundButton = document.getElementById("soundButton");

const WIDTH = 1000;
const HEIGHT = 650;
const PLAYER_SIZE = 150;
const SMASH_SIZE = 100;
const LEVEL_TARGETS = [50, 70, 100];
const COLORS = {
  black: "#000000",
  white: "#ffffff",
  green: "#9bf964",
  yellow: "#ffde00",
};

const assetPaths = {
  player: "resources/minion.png",
  menu: "resources/bg001.png",
  level1: "resources/level1.jpg",
  level2: "resources/level2.jpg",
  level3: "resources/level3.jpg",
  banana1: "resources/banana.png",
  banana2: "resources/banana_facingright.png",
  banana3: "resources/three_bananas.png",
  banana4: "resources/three_bananas_facing_right.png",
  smash1: "resources/smash.png",
  smash2: "resources/smashed.png",
};

const images = {};
const audio = new Audio("resources/min.mp3");
audio.loop = true;
audio.volume = 0.45;
let soundEnabled = false;

let mode = "main_menu";
let currentLevel = 1;
let points = 0;
let lives = 5;
let speed = 2;
let lastSpawn = 0;
let spawnDelay = 400;
let pointerX = WIDTH / 2;
let enemies = [];
let smashedBananas = [];
let decorativeSpawn = 0;
let lastFrame = performance.now();

const player = {
  x: WIDTH / 2 - PLAYER_SIZE / 2,
  y: HEIGHT - PLAYER_SIZE,
  width: PLAYER_SIZE,
  height: PLAYER_SIZE,
};

function loadImage(src) {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.onload = () => resolve(image);
    image.onerror = () => reject(new Error(`Could not load ${src}`));
    image.src = src;
  });
}

async function loadAssets() {
  const entries = Object.entries(assetPaths);
  await Promise.all(entries.map(async ([key, path]) => {
    images[key] = await loadImage(path);
  }));
  await document.fonts.ready;
  loadingMessage.remove();
  requestAnimationFrame(gameLoop);
}

function randomChoice(values) {
  return values[Math.floor(Math.random() * values.length)];
}

function bananaImages() {
  return [images.banana1, images.banana2, images.banana3, images.banana4];
}

function spawnBanana(fallSpeed = speed) {
  const image = randomChoice(bananaImages());
  const width = image.naturalWidth;
  const height = image.naturalHeight;
  enemies.push({
    image,
    x: Math.random() * Math.max(1, WIDTH - width),
    y: -height,
    width,
    height,
    speed: fallSpeed,
  });
}

function updateCanvasCursor() {
  canvas.style.cursor = mode === "game" ? "crosshair" : "pointer";
}

function resetGame() {
  currentLevel = 1;
  points = 0;
  lives = 5;
  speed = 2;
  enemies = [];
  smashedBananas = [];
  lastSpawn = performance.now();
  mode = "game";
  updateCanvasCursor();
}

function startNextLevel() {
  currentLevel += 1;
  points = 0;
  lives = 5;
  speed = 1 + currentLevel;
  enemies = [];
  smashedBananas = [];
  lastSpawn = performance.now();
  mode = "game";
  updateCanvasCursor();
}

function drawImageCover(image) {
  const scale = Math.max(WIDTH / image.naturalWidth, HEIGHT / image.naturalHeight);
  const width = image.naturalWidth * scale;
  const height = image.naturalHeight * scale;
  ctx.drawImage(image, (WIDTH - width) / 2, (HEIGHT - height) / 2, width, height);
}

function drawText(text, x, y, size, color, family = "Galactica", align = "center") {
  ctx.save();
  ctx.font = `${size}px ${family}, sans-serif`;
  ctx.fillStyle = color;
  ctx.textAlign = align;
  ctx.textBaseline = "middle";
  ctx.fillText(text, x, y);
  ctx.restore();
}

function buttonRect(centerX, centerY, width, height) {
  return { x: centerX - width / 2, y: centerY - height / 2, width, height };
}

function pointInRect(x, y, rect) {
  return x >= rect.x && x <= rect.x + rect.width && y >= rect.y && y <= rect.y + rect.height;
}

function drawButton(label, rect) {
  const hovered = pointInRect(pointerX, HEIGHT / 2, rect);
  ctx.fillStyle = hovered ? COLORS.green : COLORS.yellow;
  ctx.fillRect(rect.x, rect.y, rect.width, rect.height);
  drawText(label, rect.x + rect.width / 2, rect.y + rect.height / 2, 30, COLORS.black);
}

function intersects(a, b) {
  return a.x < b.x + b.width && a.x + a.width > b.x && a.y < b.y + b.height && a.y + a.height > b.y;
}

function updatePlayer() {
  player.x = Math.max(0, Math.min(WIDTH - player.width, pointerX - player.width / 2));
}

function updateEnemies(deltaScale) {
  const survivors = [];
  for (const enemy of enemies) {
    enemy.y += enemy.speed * deltaScale;

    if (mode === "game" && intersects(player, enemy)) {
      points += 1;
      continue;
    }

    if (enemy.y + enemy.height > HEIGHT) {
      if (mode === "game") {
        lives -= 1;
        smashedBananas.push({
          image: Math.random() < 0.5 ? images.smash1 : images.smash2,
          x: enemy.x,
          y: Math.min(enemy.y, HEIGHT - SMASH_SIZE),
        });
      }
      continue;
    }

    survivors.push(enemy);
  }
  enemies = survivors;
}

function drawEnemies() {
  for (const enemy of enemies) {
    ctx.drawImage(enemy.image, enemy.x, enemy.y, enemy.width, enemy.height);
  }
}

function drawMenu(now, deltaScale) {
  drawImageCover(images.menu);
  drawText("CATCH THE BANANA", WIDTH / 2, 100, 76, COLORS.black, "Yoster");
  drawText("Move the minion and do not drop the bananas!", WIDTH / 2, 195, 20, COLORS.black);

  if (now - decorativeSpawn > 550 && enemies.length < 6) {
    spawnBanana(1);
    decorativeSpawn = now;
  }
  updateEnemies(deltaScale);
  drawEnemies();

  const rect = buttonRect(WIDTH / 2, 330, 300, 100);
  ctx.fillStyle = COLORS.yellow;
  ctx.fillRect(rect.x, rect.y, rect.width, rect.height);
  drawText("PRESS TO START", WIDTH / 2, 330, 28, COLORS.black);
}

function drawGame(now, deltaScale) {
  drawImageCover(images[`level${currentLevel}`]);

  for (const smash of smashedBananas) {
    ctx.drawImage(smash.image, smash.x, smash.y, SMASH_SIZE, SMASH_SIZE);
  }

  if (now - lastSpawn >= spawnDelay) {
    spawnBanana();
    lastSpawn = now;
  }

  updatePlayer();
  updateEnemies(deltaScale);

  ctx.drawImage(images.player, player.x, player.y, player.width, player.height);
  drawEnemies();

  const hudColor = currentLevel === 2 ? COLORS.white : COLORS.black;
  drawText(`POINTS: ${points}`, WIDTH / 2, 24, 28, hudColor);
  drawText(`LIVES: ${lives}`, WIDTH - 145, 24, 28, hudColor);
  drawText(`LEVEL ${currentLevel}`, 110, 24, 24, hudColor);

  if (lives <= 0) {
    mode = "final_screen";
    enemies = [];
  } else if (points >= LEVEL_TARGETS[currentLevel - 1]) {
    enemies = [];
    mode = currentLevel < 3 ? "level_complete" : "win_screen";
  }
}

function drawLevelComplete() {
  drawImageCover(images[`level${currentLevel}`]);
  drawText(`LEVEL ${currentLevel} COMPLETE!`, WIDTH / 2, 205, 40, COLORS.white);
  drawText("Ready for the next one?", WIDTH / 2, 295, 30, COLORS.white);
  const rect = buttonRect(WIDTH / 2, 415, 300, 100);
  ctx.fillStyle = COLORS.yellow;
  ctx.fillRect(rect.x, rect.y, rect.width, rect.height);
  drawText("YES", WIDTH / 2, 415, 32, COLORS.black);
}

function drawWinScreen() {
  drawImageCover(images.level3);
  drawText("CONGRATULATIONS!", WIDTH / 2, 205, 68, COLORS.black, "Yoster");
  drawText("You completed all three levels!", WIDTH / 2, 385, 30, COLORS.black);
  drawText("Click anywhere to play again", WIDTH / 2, 455, 22, COLORS.black);
}

function drawFinalScreen() {
  drawImageCover(images.menu);
  drawText("YOU LOST.", WIDTH / 2, 120, 78, COLORS.black, "Yoster");
  drawText("Click or press any key to restart", WIDTH / 2, 400, 30, COLORS.black);
}

function gameLoop(now) {
  const delta = Math.min(32, now - lastFrame);
  const deltaScale = delta / (1000 / 60);
  lastFrame = now;

  ctx.clearRect(0, 0, WIDTH, HEIGHT);

  if (mode === "main_menu") drawMenu(now, deltaScale);
  if (mode === "game") drawGame(now, deltaScale);
  if (mode === "level_complete") drawLevelComplete();
  if (mode === "win_screen") drawWinScreen();
  if (mode === "final_screen") drawFinalScreen();

  requestAnimationFrame(gameLoop);
}

function canvasCoordinates(clientX, clientY) {
  const rect = canvas.getBoundingClientRect();
  return {
    x: (clientX - rect.left) * (WIDTH / rect.width),
    y: (clientY - rect.top) * (HEIGHT / rect.height),
  };
}

function movePointer(clientX, clientY) {
  const point = canvasCoordinates(clientX, clientY);
  pointerX = point.x;
}

function activate(clientX, clientY) {
  const point = canvasCoordinates(clientX, clientY);
  pointerX = point.x;

  if (mode === "main_menu") {
    resetGame();
  } else if (
    mode === "level_complete" &&
    pointInRect(
      point.x,
      point.y,
      buttonRect(WIDTH / 2, 415, 300, 100)
    )
  ) {
    startNextLevel();
  } else if (mode === "win_screen" || mode === "final_screen") {
    enemies = [];
    smashedBananas = [];
    mode = "main_menu";
    updateCanvasCursor();
  }
}

canvas.addEventListener("mousemove", (event) => movePointer(event.clientX, event.clientY));
canvas.addEventListener("click", (event) => activate(event.clientX, event.clientY));
canvas.addEventListener("touchstart", (event) => {
  event.preventDefault();
  const touch = event.touches[0];
  movePointer(touch.clientX, touch.clientY);
  activate(touch.clientX, touch.clientY);
}, { passive: false });
canvas.addEventListener("touchmove", (event) => {
  event.preventDefault();
  const touch = event.touches[0];
  movePointer(touch.clientX, touch.clientY);
}, { passive: false });

window.addEventListener("keydown", () => {
  if (mode === "final_screen" || mode === "win_screen") {
    enemies = [];
    smashedBananas = [];
    mode = "main_menu";
    updateCanvasCursor();
  }
});

soundButton.addEventListener("click", async () => {
  soundEnabled = !soundEnabled;
  soundButton.setAttribute("aria-pressed", String(soundEnabled));
  soundButton.textContent = `Sound: ${soundEnabled ? "On" : "Off"}`;
  if (soundEnabled) {
    try {
      await audio.play();
    } catch (error) {
      console.warn("Audio playback was blocked by the browser.", error);
    }
  } else {
    audio.pause();
  }
});
updateCanvasCursor();

loadAssets().catch((error) => {
  console.error(error);
  loadingMessage.textContent = "The game could not load. Check that the resources folder is present.";
});
