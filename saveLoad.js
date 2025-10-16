// saveLoad.js

// Функция для сохранения игры
export function saveGame(player, currentLevel, levels) {
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
        return "Игра успешно сохранена!";
    } catch (error) {
        console.error('Ошибка при сохранении игры:', error);
        return "Не удалось сохранить игру. Пожалуйста, попробуйте еще раз.";
    }
}

// Функция для загрузки игры
export function loadGame(player, Level, Attic) {
    try {
        const savedState = localStorage.getItem('gameState');
        if (savedState) {
            const gameState = JSON.parse(savedState);
            
            // Загрузка данных игрока
            Object.assign(player, gameState.player);
            
            const currentLevel = gameState.currentLevel;
            
            // Пересоздание уровней
            const levels = gameState.levels.map((levelData, index) => {
                let level;
                if (levelData.type === 'Attic') {
                    level = new Attic();
                } else {
                    level = new Level(60, 40); // Используем константы GRID_WIDTH и GRID_HEIGHT
                }
                level.level = levelData.level;
                level.items = levelData.items;
                level.visibilityMap = levelData.visibilityMap;
                level.firstVisit = levelData.firstVisit;
                level.entrance = levelData.entrance;
                level.exit = levelData.exit;
                return level;
            });

            return {
                message: "Игра успешно загружена!",
                currentLevel: currentLevel,
                levels: levels
            };
        } else {
            return {
                message: "Сохраненная игра не найдена.",
                currentLevel: null,
                levels: null
            };
        }
    } catch (error) {
        console.error('Ошибка при загрузке игры:', error);
        return {
            message: "Не удалось загрузить игру. Возможно, сохранение повреждено.",
            currentLevel: null,
            levels: null
        };
    }
}

// Функция для проверки наличия сохранения
export function hasSavedGame() {
    return localStorage.getItem('gameState') !== null;
}
