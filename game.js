// Константы
const GRID_WIDTH = 60;
const GRID_HEIGHT = 40;
const TILE_SIZE = 20;
const EMPTY = 0;
const WALL = 1;
const ENTRANCE = 2;
const EXIT = 3;
const STAIRS_DOWN = 4;
const STAIRS_UP = 5;
const SPIKES = 6;
const BED = 7;
const ITEM_TYPES = ['батарейка', 'бутерброд', 'вода', 'камень', 'ножик', 'палка', 'кирка', 'записка', 'аптечка'];
const notesText = [
    "В темноте светится только правда.",
    "Кто ищет, тот всегда найдёт.",
    "Здесь что-то скрывается... будь осторожен.",
    "Кажется, кто-то был здесь до тебя.",
    "Эта лестница ведёт куда-то глубже...",
    "Запомни, каждый шаг имеет значение.",
    "Ты на верном пути.",
    "Я здесь уже третий день. Еды почти не осталось",
    "Не спускайтесь в подвал!",
    "Ключ под ковриком у двери 237",
    "Если ты это читаешь, беги!",
    "Здесь был Вася.",
    "Я слышу шаги за стеной...",
    "Не верь тому, что видишь.",
    "Выхода нет.",
	"Не оглядывайся назад.",
	'Здесь слишком темно, будь осторожен.',
    'Не забудь запастись едой и водой.',
    'Внизу могут быть ловушки, проверяй каждый шаг.',
    'Кирка пригодится для создания прохода.',
    'Привидения боятся света, держи фонарик включенным.'
];

// Глобальные переменные
let gameMessage = '';
let gameLoopId;
let gameRunning = false;
let player;
let levels = [];
let currentLevel = 16;

// Настройка canvas
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
canvas.width = GRID_WIDTH * TILE_SIZE;
canvas.height = GRID_HEIGHT * TILE_SIZE;

// Стартовое окно
const startMenuCanvas = document.getElementById('startMenuCanvas');
const startMenuCtx = startMenuCanvas.getContext('2d');
startMenuCanvas.width = 800;
startMenuCanvas.height = 800;

// Настройка информационного поля
const infoCanvas = document.getElementById('infoCanvas');
const infoCtx = infoCanvas.getContext('2d');
infoCanvas.width = 300;
infoCanvas.height = canvas.height;
infoCanvas.style.position = 'absolute';
infoCanvas.style.left = `${canvas.width + 10}px`; // Смещение справа от игрового поля на 10px
infoCanvas.style.top = `${canvas.offsetTop}px`;

// Функция инициализации игры
function initGame() {
    // Скрываем игровой canvas и info canvas
    canvas.style.display = 'none';
    infoCanvas.style.display = 'none';
    
    // Показываем стартовое меню
    startMenuCanvas.style.display = 'block';
    
    // Отрисовываем стартовое меню
    drawStartMenu();
    
    // Добавляем обработчик клавиш для стартового меню
    document.addEventListener('keydown', handleStartMenuInput);
}

// Функция отображения стартового меню
function drawStartMenu() {
    startMenuCtx.clearRect(0, 0, startMenuCanvas.width, startMenuCanvas.height);
    startMenuCtx.fillStyle = 'black';
    startMenuCtx.font = '20px Arial';
    startMenuCtx.fillText("Стартовое меню:", 50, 50);
    startMenuCtx.fillText("1. Старт новой игры", 50, 100);
    startMenuCtx.fillText("2. Загрузка предыдущих сохранений", 50, 150);
    startMenuCtx.fillText("3. Настройки игры", 50, 200);
    startMenuCtx.fillText("4. Профиль Игрока", 50, 250);
    startMenuCtx.fillText("5. Выход из игры", 50, 300);
}
// Обработчик ввода для стартового меню
function handleStartMenuInput(e) {
    switch (e.key) {
        case '1':
            startMenuCanvas.style.display = 'none';
            canvas.style.display = 'block';
            infoCanvas.style.display = 'block';
            initNewGame();
            break;
        case '2':
            loadGame();
            break;
        case '3':
            gameMessage = "Настройки игры (в разработке)";
            break;
        case '4':
            gameMessage = "Профиль Игрока (в разработке)";
            break;
        case '5':
            gameMessage = "Выход из игры";
            // Здесь можно добавить логику для выхода из игры
            break;
        default:
            return;
    }
    document.removeEventListener('keydown', handleStartMenuInput);
    if (gameRunning) {
        gameLoopId = requestAnimationFrame(gameLoop);
    }
}

// Вызов функции инициализации при загрузке страницы
window.onload = initGame;

//видимостью канвасов
startMenuCanvas.style.display = 'block';
canvas.style.display = 'none';
infoCanvas.style.display = 'none';

// Обновленная функция initNewGame
function initNewGame() {
    levels = [
        ...Array.from({ length: 15 }, (_, i) => new Level(GRID_WIDTH, GRID_HEIGHT, undefined, undefined, false, false)), // Уровни 0-14
        new Attic() // Уровень 15 (Чердак)
    ];
    currentLevel = 15; // Начинаем с Чердака
    const attic = levels[15]; // Доступ к "Чердаку" по индексу 15
    player = new Player(attic.entrance.x, attic.entrance.y);
    gameMessage = 'Начало новой игры. Добро пожаловать на Чердак!';
    gameRunning = true;
    updateVisibility();
    draw();
    drawInfoPanel();
}


// Класс игрока
class Player {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.health = 100;
        this.endurance = 100;
        this.thirst = 100;
        this.clarity = 100;
        this.backpack = [];
        this.selectedItem = -1;
        this.steps = 0;
        this.hasTakenSpikeDamage = false;
        this.hasTakenGhostDamage = false;
    }
    move(dx, dy, levelData) {
        const newX = this.x + dx;
        const newY = this.y + dy;

        if (newX >= 0 && newX < GRID_WIDTH && newY >= 0 && newY < GRID_HEIGHT) {
            const cellType = levelData.level[newY][newX];

            if (cellType === WALL) {
                gameMessage = "Вы не можете пройти сквозь стену!";
                return;
            }
            // Обновляем позицию игрока
            this.x = newX;
            this.y = newY;
            this.steps++;
            // Обновляем характеристики здоровья и выносливости
            this.updateStats();
            // Проверяем взаимодействие с ловушками
            if (cellType === SPIKES) {
                this.takeSpikeDamage(levelData, newX, newY);
            }
            // Проверка на лестницы
            if (cellType === STAIRS_DOWN) {
                changeLevel('down');
            } else if (cellType === STAIRS_UP) {
                changeLevel('up');
            }
            // Обновляем видимость после шага игрока
            updateVisibility();
            // Проверка на взаимодействие с Привидением
            interactWithGhost();
            // Проверка на сбор предметов
            this.collectItem(newX, newY, levelData);
            // Проверка на достижение выхода
          /*   if (cellType === EXIT) {
                gameMessage = `Поздравляем! Вы достигли выхода и прошли игру!`;
                gameRunning = false;
            } */
            checkPlayerDeath();
        }
    }
//уменьшение здоровья и силы каждые % шагов
    updateStats() {
        if (this.steps % 5 === 0) {
            this.endurance = Math.max(0, this.endurance - 1);
        }

        if (this.steps % 25 === 0) {
            this.health = Math.max(0, this.health - 1);
        }
    }

    takeSpikeDamage(levelData, x, y) {
        if (!this.hasTakenSpikeDamage) {
            this.health -= 10;
            gameMessage = "Вы наступили на шипы! Здоровье: " + this.health;
            levelData.level[y][x] = EMPTY;
            this.hasTakenSpikeDamage = true;
        } else {
            this.hasTakenSpikeDamage = false;
        }
    }

    collectItem(x, y, levelData) {
        const itemIndex = levelData.items.findIndex(item => item.x === x && item.y === y);
        if (itemIndex !== -1) {
            const item = levelData.items[itemIndex];
            if (item.type === 'записка') {
                const noteIndex = Math.floor(Math.random() * notesText.length);
                gameMessage = `Вы нашли записку: "${notesText[noteIndex]}"`;
            } else if (this.backpack.length < 5) {
                if (item.type === 'кирка') {
                    this.backpack.push({ type: item.type, durability: 3 });
                } else {
                    this.backpack.push({ type: item.type });
                }
                levelData.items.splice(itemIndex, 1);
                gameMessage = `Вы нашли: ${item.type}`;
            } else {
                gameMessage = "Рюкзак полон! Выберите предмет для замены или выбросите что-нибудь.";
            }
        }
    }
}
// Класс уровня
class Level {
    constructor(width, height, entranceX, entranceY, isFirstLevel = false, isLastLevel = false) {
        //console.log(`Создается уровень: ширина=${width}, высота=${height}, isFirstLevel=${isFirstLevel}, isLastLevel=${isLastLevel}`);
        this.width = width;
        this.height = height;
        this.level = Array.from({ length: height }, () => Array(width).fill(EMPTY));
        this.items = [];
        this.entrance = this.generateEntrance(entranceX, entranceY);
        this.exit = this.generateExit(this.entrance);
        this.stairsGenerated = false; // Инициализация флага
        // Генерация лестниц на всех уровнях, кроме Чердака
        if (!this.stairsGenerated) {
            this.generateStairs();
            this.stairsGenerated = true;
        }
        // Размещение главного артефакта на первом уровне
        if (isFirstLevel) {
            this.placeMainArtifact(); // Разместить главный артефакт на 1-м уровне
        }
		// Генерация стен и случайных предметов на уровне
        this.generateWallsAndItems();
		this.generateBorders();
        this.visibilityMap = Array.from({ length: height }, () => Array(width).fill(false));
        this.firstVisit = true;
    
        // Генерация границ уровня (рамки)
        this.generateBorders();
        // Инициализация карты видимости
        this.visibilityMap = Array.from({ length: height }, () => Array(width).fill(false));
		this.firstVisit = true; // Добавляем этот флаг
    }
    placeMainArtifact() {
        // Размещаем главный артефакт в центре уровня
        const centerX = Math.floor(this.width / 2);
        const centerY = Math.floor(this.height / 2);
        this.items.push({ x: centerX, y: centerY, type: 'главный артефакт' });
    }
     generateEntrance(entranceX, entranceY) {
        return {
            x: entranceX !== undefined ? entranceX : Math.floor(Math.random() * (this.width - 2)) + 1,
            y: entranceY !== undefined ? entranceY : Math.floor(Math.random() * (this.height - 2)) + 1,
        };
    }
    generateExit(entrance) {
        let exit;
        do {
            exit = {
                x: Math.floor(Math.random() * (this.width - 2)) + 1,
                y: Math.floor(Math.random() * (this.height - 2)) + 1,
            };
        } while (exit.x === entrance.x && exit.y === entrance.y);
        this.level[exit.y][exit.x] = EXIT;
        return exit;
    }
// Генерация лестниц
generateStairs() {
Level.prototype.generateStairs = function() {
    if (this.stairsGenerated) {
        return; // Если лестницы уже сгенерированы, ничего не делаем
    }
    
    console.log(`Генерация лестниц для уровня ${currentLevel}`);
    
    if (currentLevel === 0) {
        // Уровень 0: добавляем только лестницу наверх
        const stairsUpX = Math.floor(Math.random() * (this.width - 2)) + 1;
        const stairsUpY = Math.floor(Math.random() * (this.height - 2)) + 1;
        this.level[stairsUpY][stairsUpX] = STAIRS_UP;
        console.log(`Уровень 0: Лестница вверх добавлена на (${stairsUpX}, ${stairsUpY})`);
    } else if (currentLevel >= 1 && currentLevel < 16) {
        // Уровни от 1 до 15: добавляем лестницы вверх и вниз
        const stairsDownX = Math.floor(Math.random() * (this.width - 2)) + 1;
        const stairsDownY = Math.floor(Math.random() * (this.height - 2)) + 1;
        this.level[stairsDownY][stairsDownX] = STAIRS_DOWN;
        console.log(`Уровень ${currentLevel}: Лестница вниз добавлена на (${stairsDownX}, ${stairsDownY})`);

        const stairsUpX = Math.floor(Math.random() * (this.width - 2)) + 1;
        const stairsUpY = Math.floor(Math.random() * (this.height - 2)) + 1;
        this.level[stairsUpY][stairsUpX] = STAIRS_UP;
        console.log(`Уровень ${currentLevel}: Лестница вверх добавлена на (${stairsUpX}, ${stairsUpY})`);
    } else if (currentLevel === 16) {
        // Чердак: добавляем только лестницу вниз
        const stairsDownX = Math.floor(Math.random() * (this.width - 2)) + 1;
        const stairsDownY = Math.floor(Math.random() * (this.height - 2)) + 1;
        this.level[stairsDownY][stairsDownX] = STAIRS_DOWN;
        console.log(`Чердак: Лестница вниз добавлена на (${stairsDownX}, ${stairsDownY})`);
    }

    // Отмечаем, что лестницы были сгенерированы
    this.stairsGenerated = true;
};

}
    
	generateWallsAndItems() {
Level.prototype.generateWallsAndItems = function() {
    // Проверяем, является ли уровень Чердаком, и если да, то не генерируем предметы
    if (this instanceof Attic) {
        return; // Прекращаем выполнение функции для Чердака
    }

    // Генерация стен и случайных предметов на уровне
    for (let y = 1; y < this.height - 1; y++) {
        for (let x = 1; x < this.width; x++) {
            if (this.level[y][x] === EMPTY && !(x === this.exit.x && y === this.exit.y) && !(x === this.entrance.x && y === this.entrance.y)) {
                if (Math.random() < 0.3) {
                    this.level[y][x] = WALL;
                } else if (Math.random() < 0.05) {
                    const itemType = ITEM_TYPES[Math.floor(Math.random() * ITEM_TYPES.length)];
                    this.items.push({ x, y, type: itemType });
                } else if (Math.random() < 0.02) {
                    this.level[y][x] = SPIKES;
                }
            }
        }
    }
};
	}

    generateBorders() {
        for (let x = 0; x < this.width; x++) {
            this.level[0][x] = this.level[this.height - 1][x] = WALL;
        }
        for (let y = 0; y < this.height; y++) {
            this.level[y][0] = this.level[y][this.width - 1] = WALL;
        }
    }
}
// Класс Чердака
class Attic extends Level {
    constructor() {
        super(12, 8, 1, 1, false, true);
        console.log('Создан уровень "Чердак"');
        
        this.level = Array.from({ length: this.height }, () => Array(this.width).fill(EMPTY));
        this.generateBorders();
        this.entrance = { x: 1, y: 1 };
        this.level[this.height - 2][this.width - 2] = STAIRS_DOWN;
        this.visibilityMap = Array.from({ length: this.height }, () => Array(this.width).fill(true));
      
        // Добавляем кровать на Чердак
        this.level[3][3] = BED;
    }
}

// Функция для взаимодействия с кроватью
function interactWithBed() {
    if (levels[currentLevel] instanceof Attic && levels[currentLevel].level[player.y][player.x] === BED) {
        showSaveMenu();
    }
}

// Функция для отображения меню сохранения
function showSaveMenu() {
    gameMessage = "Меню сохранения: [S] Сохранить игру, [L] Загрузить игру, [C] Отмена, [Q] Выйти из игры";
    document.addEventListener('keydown', handleSaveMenuInput);
}

// Обновленная функция handleSaveMenuInput
function handleSaveMenuInput(e) {
    switch (e.key.toLowerCase()) {
        case 's':
            saveGame();
            break;
        case 'l':
            loadGame();
            break;
        case 'c':
            gameMessage = "Вы отменили действие.";
            break;
        case 'q':
            saveGame();
            gameMessage = "Вы вышли из игры. Игра сохранена.";
            gameRunning = false;
            cancelAnimationFrame(gameLoopId);
            showStartMenu();
            break;
        default:
            return;
    }
    document.removeEventListener('keydown', handleSaveMenuInput);
    // Обновляем состояние игры после загрузки
    draw();
    drawInfoPanel();
}

// Улучшенная функция сохранения игры
function saveGame() {
    const gameState = {
        player: {
            x: player.x,
            y: player.y,
            health: player.health,
            endurance: player.endurance,
            thirst: player.thirst,
            clarity: player.clarity,
            backpack: player.backpack,
            selectedItem: player.selectedItem,
            steps: player.steps
        },
        currentLevel: currentLevel,
        levels: levels.map(level => ({
            type: level instanceof Attic ? 'Attic' : 'Level',
            level: level.level,
            items: level.items,
            visibilityMap: level.visibilityMap,
            firstVisit: level.firstVisit,
            entrance: level.entrance,
            exit: level.exit
        }))
    };
    
    try {
        localStorage.setItem('gameState', JSON.stringify(gameState));
        gameMessage = "Игра успешно сохранена!";
    } catch (error) {
        console.error('Ошибка при сохранении игры:', error);
        gameMessage = "Не удалось сохранить игру. Пожалуйста, попробуйте еще раз.";
    }
}

// Улучшенная функция загрузки игры
function loadGame() {
    try {
        const savedState = localStorage.getItem('gameState');
        if (savedState) {
            const gameState = JSON.parse(savedState);
            
            // Загрузка данных игрока
            Object.assign(player, gameState.player);
            
            currentLevel = gameState.currentLevel;
            
            // Пересоздание уровней
            levels = gameState.levels.map((levelData, index) => {
                let level;
                if (levelData.type === 'Attic') {
                    level = new Attic();
                } else {
                    level = new Level(GRID_WIDTH, GRID_HEIGHT);
                }
                level.level = levelData.level;
                level.items = levelData.items;
                level.visibilityMap = levelData.visibilityMap;
                level.firstVisit = levelData.firstVisit;
                level.entrance = levelData.entrance;
                level.exit = levelData.exit;
                return level;
            });
            gameMessage = "Игра успешно загружена!";
            gameRunning = true;
            // Обновляем видимость текущего уровня
            updateVisibility();
            draw();
            drawInfoPanel();
        } else {
            gameMessage = "Сохраненная игра не найдена.";
        }
    } catch (error) {
        console.error('Ошибка при загрузке игры:', error);
        gameMessage = "Не удалось загрузить игру. Возможно, сохранение повреждено.";
        initNewGame();
    }
}
// Функция для проверки совместимости сохранения
function checkSaveCompatibility(savedState) {
    // Здесь можно добавить проверки на соответствие версии сохранения
    // текущей версии игры, наличие необходимых полей и т.д.
    return true; // Возвращаем true, если сохранение совместимо
}

// Обновление механики видимости
Level.prototype.initVisibility = function() {
    if (this instanceof Attic) {
        this.visibilityMap = Array.from({ length: this.height }, () => Array(this.width).fill(true)); // Полная видимость на уровне Чердак
    } else if (this.firstVisit) {
        this.visibilityMap = Array.from({ length: this.height }, () => Array(this.width).fill(false)); // Полностью скрыт при первом посещении
        this.firstVisit = false; // Отмечаем, что уровень был посещен
    }
    // Если это не первое посещение, оставляем visibilityMap как есть
};

Level.prototype.saveVisibility = function(visibilityMap) {
    this.visibilityMap = visibilityMap;
};
function changeLevel(newLevelIndex) {
    // Сохраняем видимость текущего уровня перед переходом
    levels[currentLevel].saveVisibility(player.visibilityMap);
    // Меняем уровень
    currentLevel = newLevelIndex;
    const newLevel = levels[currentLevel];
    // Инициализируем видимость на новом уровне
    newLevel.initVisibility();
    // Устанавливаем игрока на входную точку нового уровня
    player.x = newLevel.entrance.x;
    player.y = newLevel.entrance.y;
    player.visibilityMap = newLevel.visibilityMap;
    //console.log(`Игрок перешел на уровень ${currentLevel}`);
}
// Обновление уровня и переход на другой уровень
function changeLevel(direction) {
     // Сохраняем видимость текущего уровня перед переходом
    levels[currentLevel].saveVisibility(levels[currentLevel].visibilityMap);
	if (currentLevel === 16 && direction === 'down') {
        // Переход с Чердака на 15 этаж
        currentLevel = 15;
        moveToNewLevel();
    } else if (currentLevel === 15) {
        if (direction === 'up') {
            // Переход с 15 этажа на Чердак
            currentLevel = 16;
            moveToNewLevel();
        } else if (direction === 'down') {
            // Переход с 15 этажа на 14 этаж
            currentLevel = 14;
            moveToNewLevel();
        }
    } else if (currentLevel >= 1 && currentLevel <= 14) {
        if (direction === 'up') {
            // Подъем на этаж выше
            currentLevel++;
            moveToNewLevel();
        } else if (direction === 'down') {
            // Спуск на этаж ниже
            currentLevel--;
            moveToNewLevel();
        }
    } else if (currentLevel === 0 && direction === 'up') {
        // Переход с уровня 0 на уровень 1
        currentLevel = 1;
        moveToNewLevel();
    }
}
// видимость на уровне
function moveToNewLevel() {
    const newLevel = levels[currentLevel];
    player.x = newLevel.entrance.x;
    player.y = newLevel.entrance.y;
    if (currentLevel === 16) { // Уровень "Чердак"
        gameMessage = 'Вы находитесь на уровне Чердак';
        newLevel.visibilityMap = Array.from({ length: newLevel.height }, () => Array(newLevel.width).fill(true));
    } else {
        gameMessage = `Вы ${currentLevel < 15 ? 'спустились' : 'поднялись'} на уровень ${currentLevel}`;
        newLevel.initVisibility(); // Инициализируем видимость в зависимости от того, первое это посещение или нет
    }
    // Обновляем видимость вокруг игрока
    updateVisibility();
}
// Оптимизация обработки событий клавиатуры
function handleKeyEvent(e) {
    if (!gameRunning) return;
    switch (e.key) {
        case 'ArrowUp':
            player.move(0, -1, levels[currentLevel]);
            break;
        case 'ArrowDown':
            player.move(0, 1, levels[currentLevel]);
            break;
        case 'ArrowLeft':
            player.move(-1, 0, levels[currentLevel]);
            break;
        case 'ArrowRight':
            player.move(1, 0, levels[currentLevel]);
            break;
        case 'G': case 'g':
            usePickaxe();
            break;
        case 'u': case 'U':
            useItem();
            break;
        case 'd': case 'D':
            dropItem();
            break;
        case '1': case '2': case '3': case '4': case '5':
            selectItem(parseInt(e.key) - 1);
            break;
			case 'e': case 'E': // Добавляем клавишу для взаимодействия
        interactWithBed();
        break;
    }
}

document.addEventListener('keydown', handleKeyEvent);
// Игровой цикл
function gameLoop() {
    if (!gameRunning) return;
    draw();
    drawInfoPanel();
    gameLoopId = requestAnimationFrame(gameLoop);
}
// Функция отрисовки уровня
function draw() {
    // Очистка канвы
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const currentLevelData = levels[currentLevel];
    const currentVisibilityMap = currentLevelData.visibilityMap;
    const currentWidth = currentLevelData.width;
    const currentHeight = currentLevelData.height;

 // Отрисовка уровня
    for (let y = 0; y < currentHeight; y++) {
        for (let x = 0; x < currentWidth; x++) {
            if (currentVisibilityMap[y][x]) {
                switch (currentLevelData.level[y][x]) {
                    case WALL:
                        ctx.fillStyle = 'gray';
                        ctx.fillRect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE);
                        break;
                    case SPIKES:
                        ctx.fillStyle = 'red';
                        ctx.fillRect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE);
                        ctx.fillStyle = 'black';
                        ctx.fillText('^', x * TILE_SIZE + TILE_SIZE / 4, y * TILE_SIZE + 3 * TILE_SIZE / 4);
                        break;
                    case ENTRANCE:
                        ctx.fillStyle = 'limegreen';
                        ctx.fillRect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE);
                        break;
 /*                    case EXIT:
                        ctx.fillStyle = 'gold';
                        ctx.fillRect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE);
                        break; */
                    case STAIRS_DOWN:
                        ctx.fillStyle = 'purple';
                        ctx.fillRect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE);
                        ctx.fillStyle = 'white';
                        ctx.fillText('↓', x * TILE_SIZE + 5, y * TILE_SIZE + TILE_SIZE - 5);
                        break;
                    case STAIRS_UP:
                        ctx.fillStyle = 'orange';
                        ctx.fillRect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE);
                        ctx.fillStyle = 'white';
                        ctx.fillText('↑', x * TILE_SIZE + 5, y * TILE_SIZE + TILE_SIZE - 5);
                        break;
                    default:
                        ctx.fillStyle = 'white';
                        ctx.fillRect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE);
                }
            } else {
                // Неосвещенные клетки
                ctx.fillStyle = 'black';
                ctx.fillRect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE);
            }
			// Добавляем отрисовку кровати
    if (currentLevelData.level[y][x] === BED) {
        ctx.fillStyle = 'brown';
        ctx.fillRect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE);
        ctx.fillStyle = 'white';
        ctx.fillText('🛏️', x * TILE_SIZE + TILE_SIZE / 4, y * TILE_SIZE + 3 * TILE_SIZE / 4);
    }
        }
    }

 // Отрисовка предметов
    currentLevelData.items.forEach(item => {
        if (currentVisibilityMap[item.y][item.x]) {
            ctx.fillStyle = 'black';
            ctx.fillText(getItemSymbol(item.type), item.x * TILE_SIZE + TILE_SIZE / 4, item.y * TILE_SIZE + 3 * TILE_SIZE / 4);
        }
    });

 // Отрисовка игрока 
    const playerIcon = '🧍';
    ctx.fillStyle = 'black';
    ctx.font = `${TILE_SIZE - 4}px Arial`;
    ctx.fillText(playerIcon, player.x * TILE_SIZE + TILE_SIZE / 4, player.y * TILE_SIZE + 3 * TILE_SIZE / 4);
}
// Функция отрисовки информационного поля
function drawInfoPanel() {
    // Очистка информационной панели
    infoCtx.clearRect(0, 0, infoCanvas.width, infoCanvas.height);

    const panelHeight = infoCanvas.height / 3;

    // Верхняя часть - характеристики игрока
    infoCtx.fillStyle = 'black';
    infoCtx.font = '16px Arial';
    infoCtx.fillText('Характеристики:', 10, 20);
    infoCtx.fillText('Здоровье: ' + player.health, 10, 50);
    infoCtx.fillText('Выносливость: ' + player.endurance, 10, 80);
    infoCtx.fillText('Жажда: ' + player.thirst, 10, 110);
    infoCtx.fillText('Ясность ума: ' + player.clarity, 10, 140);

    // Средняя часть - рюкзак
    infoCtx.fillText('Рюкзак:', 10, panelHeight + 20);
    player.backpack.forEach((item, index) => {
        infoCtx.fillText(`${index + 1}. ${item.type}` + (item.durability ? ` (Прочность: ${item.durability})` : ''), 10, panelHeight + 50 + index * 30);
    });

    // Нижняя часть - сообщения от игры+Раздел 'Отладка'
    infoCtx.fillText('Отладка:', 10, panelHeight * 2 + 100);
    infoCtx.fillText('Текущий уровень: ' + currentLevel, 10, panelHeight * 2 + 130);
    const exitsUp = levels[currentLevel].level.flat().filter(x => x === STAIRS_UP).length;
    const exitsDown = levels[currentLevel].level.flat().filter(x => x === STAIRS_DOWN).length;
    infoCtx.fillText('Выходов вверх: ' + exitsUp, 10, panelHeight * 2 + 160);
    infoCtx.fillText('Выходов вниз: ' + exitsDown, 10, panelHeight * 2 + 190);
    infoCtx.fillText('Сообщения:', 10, panelHeight * 2 + 20);
    wrapText(infoCtx, gameMessage, 10, panelHeight * 2 + 50, infoCanvas.width - 20, 20);
}
// Функция переноса текста для сообщений
function wrapText(context, text, x, y, maxWidth, lineHeight) {
    const words = text.split(' ');
    let line = '';
    for (let n = 0; n < words.length; n++) {
        const testLine = line + words[n] + ' ';
        const metrics = context.measureText(testLine);
        const testWidth = metrics.width;
        if (testWidth > maxWidth && n > 0) {
            context.fillText(line, x, y);
            line = words[n] + ' ';
            y += lineHeight;
        } else {
            line = testLine;
        }
    }
    context.fillText(line, x, y);
}
// Функция для получения символа предмета
function getItemSymbol(itemType) {
    switch (itemType) {
        case 'батарейка': return '⚡';
        case 'бутерброд': return '🍔';
        case 'вода': return '💧';
        case 'камень': return '🪨';
        case 'ножик': return '🔪';
        case 'палка': return '🌿';
        case 'кирка': return '⛏️';
        case 'записка': return '📜';
        case 'аптечка': return '🩹';
        default: return '?';
    }
}
// Функция для использования кирки
function usePickaxe() {
    const pickaxeIndex = player.backpack.findIndex(item => item.type === 'кирка');
    if (pickaxeIndex !== -1) {
        const pickaxe = player.backpack[pickaxeIndex];
        if (!pickaxe.durability) pickaxe.durability = 3; 
        gameMessage = "Выберите направление удара киркой: стрелки для удара вверх/вниз/влево/вправо, 'k' для создания дыры на нижнем уровне.";
        document.addEventListener('keydown', handlePickaxeDirection);
    } else {
        gameMessage = "У вас нет кирки!";
    }
}
// Функция для создания дыры на нижний уровень
function createStairsDown() {
    const targetX = player.x;
    const targetY = player.y + 1;

    if (targetY >= 0 && targetY < GRID_HEIGHT) {
        const currentLevelData = levels[currentLevel];
        
        // Проверяем, есть ли стена на нижнем уровне
        if (currentLevelData.level[targetY][targetX] === WALL) {
            gameMessage = "На уровне ниже находится стена. Разрушить стену на уровне ниже? (Y/N)";
            document.addEventListener('keydown', function handleDecision(e) {
                if (e.key.toLowerCase() === 'y') {
                    currentLevelData.level[targetY][targetX] = EMPTY;
                    gameMessage = "Вы разрушили стену и создали проход на нижний уровень.";
                    
                    // Уменьшаем прочность кирки
                    const pickaxeIndex = player.backpack.findIndex(item => item.type === 'кирка');
                    if (pickaxeIndex !== -1) {
                        const pickaxe = player.backpack[pickaxeIndex];
                        pickaxe.durability -= 2;

                        if (pickaxe.durability <= 0) {
                            player.backpack.splice(pickaxeIndex, 1);
                            gameMessage += " Кирка сломалась!";
                        }
                    }
                } else {
                    gameMessage = "Вы решили не разрушать стену.";
                }
                
                document.removeEventListener('keydown', handleDecision);
            });
        } else if (currentLevelData.level[targetY][targetX] === EMPTY) {
            currentLevelData.level[targetY][targetX] = STAIRS_DOWN;
            gameMessage = "Вы создали проход на нижний уровень.";
        } else {
            gameMessage = "Невозможно создать проход в этой ячейке.";
        }

        // Уменьшаем прочность кирки, если не было стены
        if (currentLevelData.level[targetY][targetX] === STAIRS_DOWN) {
            const pickaxeIndex = player.backpack.findIndex(item => item.type === 'кирка');
            if (pickaxeIndex !== -1) {
                const pickaxe = player.backpack[pickaxeIndex];
                pickaxe.durability--;

                if (pickaxe.durability <= 0) {
                    player.backpack.splice(pickaxeIndex, 1);
                    gameMessage += " Кирка сломалась!";
                }
            }
        }
    } else {
        gameMessage = "Некорректное направление для создания прохода.";
    }
}
// Функция для обработки направления удара киркой
function handlePickaxeDirection(e) {
    const currentLevelData = levels[currentLevel];
    let targetX = player.x; // По умолчанию позиция по горизонтали
    let targetY = player.y; // По умолчанию позиция по вертикали

    switch (e.key) {
        case 'ArrowUp':
            targetY -= 1; // Удар вверх
            break;
        case 'ArrowDown':
            targetY += 1; // Удар вниз
            break;
        case 'ArrowLeft':
            targetX -= 1; // Удар влево
            break;
        case 'ArrowRight':
            targetX += 1; // Удар вправо
            break;
        case 'k':
            createStairsDown(); // Создать дыру на нижнем уровне
            return;
        default:
            return; // Игнорируем другие клавиши
    }

    if (targetX >= 0 && targetX < GRID_WIDTH && targetY >= 0 && targetY < GRID_HEIGHT) {
        if (currentLevelData.level[targetY][targetX] === WALL) {
            currentLevelData.level[targetY][targetX] = EMPTY;
            gameMessage = "Вы разрушили стену киркой!";
        } else {
            gameMessage = "Здесь нет стены для разрушения.";
        }
    } else {
        gameMessage = "Некорректное направление.";
    }
    // Уменьшаем прочность кирки
    const pickaxeIndex = player.backpack.findIndex(item => item.type === 'кирка');
    const pickaxe = player.backpack[pickaxeIndex];
    pickaxe.durability--;

    if (pickaxe.durability <= 0) {
        player.backpack.splice(pickaxeIndex, 1);
        gameMessage += " Кирка сломалась!";
    }
    // Завершаем выбор направления
    document.removeEventListener('keydown', handlePickaxeDirection);
}
// Обработчик клавиши G для активации удара киркой
document.addEventListener('keydown', (e) => {
    if (e.key === 'G' || e.key === 'g') {
        usePickaxe();
    }
});
// функция для выбора предмета
function selectItem(index) {
    if (index < player.backpack.length) {
        player.selectedItem = index;
        const selectedItem = player.backpack[index];
        if (selectedItem.type === 'кирка') {
            usePickaxe();
        }
    }
}
// функция для использования предмета
function useItem() {
    if (player.selectedItem !== -1) {
        const item = player.backpack[player.selectedItem];
        switch (item.type) {
            case 'аптечка':
                player.health = Math.min(100, player.health + 25);
                gameMessage = "Вы использовали аптечку и восстановили здоровье.";
                player.backpack.splice(player.selectedItem, 1);
                break;
            case 'бутерброд':
                player.health = Math.min(100, player.health + 25);
                player.endurance = Math.min(100, player.endurance + 5);
                gameMessage = "Вы съели бутерброд.";
                player.backpack.splice(player.selectedItem, 1);
                break;
            case 'вода':
                player.thirst = Math.min(100, player.thirst + 20);
                gameMessage = "Вы выпили воду.";
                player.backpack.splice(player.selectedItem, 1);
                break;
            default:
                gameMessage = `Вы не можете использовать ${item.type}.`;
                break;
        }
    } else {
        gameMessage = "Вы не выбрали предмет для использования.";
    }
}
//функция для выкидывания предмета
function dropItem() {
    if (player.selectedItem !== -1) {
        const droppedItem = player.backpack.splice(player.selectedItem, 1)[0];
        gameMessage = `Вы выбросили: ${droppedItem.type}`;
        player.selectedItem = -1;
    } else {
        gameMessage = "Вы не выбрали предмет для выброса.";
    }
}
function selectItem(index) {
    if (index >= 0 && index < player.backpack.length) {
        player.selectedItem = index;
        gameMessage = `Вы выбрали: ${player.backpack[index].type}`;
    } else {
        gameMessage = "Неверный выбор предмета.";
    }
}
// Функция для обновления видимости
function updateVisibility() {
    const currentLevelVisibilityMap = levels[currentLevel].visibilityMap;
    for (let y = -2; y <= 2; y++) {
        for (let x = -2; x <= 2; x++) {
            const newX = player.x + x;
            const newY = player.y + y;

            // Проверяем, что newX и newY находятся в пределах границ уровня
            if (
                newX >= 0 && newX < GRID_WIDTH &&
                newY >= 0 && newY < GRID_HEIGHT &&
                currentLevelVisibilityMap[newY]
            ) {
                currentLevelVisibilityMap[newY][newX] = true;
            }
        }
    }
}

// Функция взаимодействия с привидением (заглушка)
function interactWithGhost() {
    // Логика для взаимодействия с привидением
}
// Проверка на смерть игрока
function checkPlayerDeath() {
    if (player.health <= 0) {
        gameMessage = "Вы мертвы";
        gameRunning = false;
        cancelAnimationFrame(gameLoopId);
    }
}

// Инициализация игры
initGame();
