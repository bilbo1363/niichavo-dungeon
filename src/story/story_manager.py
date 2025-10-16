"""
Менеджер сюжета
"""
from typing import Dict, Optional
from .dialogue_system import Dialogue, DialogueNode, DialogueChoice


class StoryManager:
    """Менеджер сюжета игры"""
    
    def __init__(self):
        """Инициализация менеджера"""
        self.dialogues: Dict[str, Dialogue] = {}
        self.story_flags: Dict[str, bool] = {}
        self.story_variables: Dict[str, int] = {}
        
        # Создаём диалоги
        self._create_dialogues()
        
    def _create_dialogues(self) -> None:
        """Создать все диалоги игры"""
        
        # Диалог при первом запуске
        self._create_intro_dialogue()
        
        # Диалог на 10 этаже
        self._create_midpoint_dialogue()
        
        # Финальный диалог
        self._create_ending_dialogue()
        
    def _create_intro_dialogue(self) -> None:
        """Вступительный диалог"""
        dialogue = Dialogue("intro", "start")
        
        dialogue.add_node("start", DialogueNode(
            speaker="Голос из темноты",
            text="Ты проснулся на чердаке старого дома. Внизу зияет провал в подземелье. Что-то тянет тебя туда...",
            choices=[
                DialogueChoice("Спуститься в подземелье", "descend"),
                DialogueChoice("Осмотреться на чердаке", "look_around"),
            ]
        ))
        
        dialogue.add_node("descend", DialogueNode(
            speaker="Внутренний голос",
            text="20 этажей подземелья ждут тебя. Каждый этаж опаснее предыдущего. Стабилизируй их все, чтобы найти выход.",
            choices=[
                DialogueChoice("Я готов", "ready"),
            ]
        ))
        
        dialogue.add_node("look_around", DialogueNode(
            speaker="Внутренний голос",
            text="На чердаке есть сундук для хранения вещей. Здесь ты в безопасности. Но ответы - внизу.",
            choices=[
                DialogueChoice("Понятно, спускаюсь", "ready"),
            ]
        ))
        
        dialogue.add_node("ready", DialogueNode(
            speaker="Внутренний голос",
            text="Помни: собирай руны устойчивости, чтобы стабилизировать этажи. Только так ты сможешь вернуться.",
            choices=[
                DialogueChoice("Начать приключение", "END"),
            ],
            on_show=lambda: self.set_flag("intro_shown", True)
        ))
        
        self.dialogues["intro"] = dialogue
        
    def _create_midpoint_dialogue(self) -> None:
        """Диалог на середине пути"""
        dialogue = Dialogue("midpoint", "start")
        
        dialogue.add_node("start", DialogueNode(
            speaker="Эхо прошлого",
            text="Ты прошёл половину пути. Чувствуешь? Подземелье живое. Оно помнит всех, кто спускался сюда.",
            choices=[
                DialogueChoice("Кто здесь был до меня?", "who"),
                DialogueChoice("Что находится на дне?", "what"),
                DialogueChoice("Продолжить молча", "END"),
            ]
        ))
        
        dialogue.add_node("who", DialogueNode(
            speaker="Эхо прошлого",
            text="Многие искатели приключений. Некоторые искали сокровища, другие - знания. Никто не вернулся.",
            choices=[
                DialogueChoice("Я буду первым", "determined"),
                DialogueChoice("Может, стоит вернуться?", "doubt"),
            ]
        ))
        
        dialogue.add_node("what", DialogueNode(
            speaker="Эхо прошлого",
            text="На дне - истина. О тебе. О подземелье. О том, почему ты здесь. Но цена знания высока.",
            choices=[
                DialogueChoice("Я готов заплатить", "determined"),
                DialogueChoice("Это звучит пугающе", "doubt"),
            ]
        ))
        
        dialogue.add_node("determined", DialogueNode(
            speaker="Эхо прошлого",
            text="Твоя решимость похвальна. Продолжай. Ответы ждут тебя на 20-м этаже.",
            choices=[
                DialogueChoice("Спасибо", "END"),
            ]
        ))
        
        dialogue.add_node("doubt", DialogueNode(
            speaker="Эхо прошлого",
            text="Сомнения - признак мудрости. Но путь назад закрыт. Только вперёд, только вниз.",
            choices=[
                DialogueChoice("Тогда я продолжу", "END"),
            ]
        ))
        
        self.dialogues["midpoint"] = dialogue
        
    def _create_ending_dialogue(self) -> None:
        """Финальный диалог"""
        dialogue = Dialogue("ending", "start")
        
        dialogue.add_node("start", DialogueNode(
            speaker="Твоё отражение",
            text="Ты дошёл до конца. Перед тобой - зеркало. В нём ты видишь себя, но... другого.",
            choices=[
                DialogueChoice("Кто ты?", "who_are_you"),
            ]
        ))
        
        dialogue.add_node("who_are_you", DialogueNode(
            speaker="Твоё отражение",
            text="Я - это ты. Та часть, которую ты оставил наверху. Подземелье было испытанием. Ты прошёл его.",
            choices=[
                DialogueChoice("Что теперь?", "what_now"),
            ]
        ))
        
        dialogue.add_node("what_now", DialogueNode(
            speaker="Твоё отражение",
            text="Теперь ты можешь вернуться. Но ты уже не тот, кем был. Ты сильнее. Ты готов к настоящему миру.",
            choices=[
                DialogueChoice("Я хочу вернуться", "return"),
                DialogueChoice("Я хочу остаться", "stay"),
            ]
        ))
        
        dialogue.add_node("return", DialogueNode(
            speaker="Твоё отражение",
            text="Мудрый выбор. Иди. Мир ждёт тебя. И помни - подземелье всегда будет здесь, если понадобится.",
            choices=[
                DialogueChoice("Прощай", "END"),
            ],
            on_show=lambda: self.set_flag("ending_return", True)
        ))
        
        dialogue.add_node("stay", DialogueNode(
            speaker="Твоё отражение",
            text="Интересно. Ты выбрал остаться. Тогда подземелье станет твоим домом. Навсегда.",
            choices=[
                DialogueChoice("Я согласен", "END"),
            ],
            on_show=lambda: self.set_flag("ending_stay", True)
        ))
        
        self.dialogues["ending"] = dialogue
        
    def get_dialogue(self, dialogue_id: str) -> Optional[Dialogue]:
        """
        Получить диалог
        
        Args:
            dialogue_id: ID диалога
            
        Returns:
            Диалог или None
        """
        return self.dialogues.get(dialogue_id)
        
    def set_flag(self, flag: str, value: bool) -> None:
        """
        Установить флаг сюжета
        
        Args:
            flag: Имя флага
            value: Значение
        """
        self.story_flags[flag] = value
        
    def get_flag(self, flag: str) -> bool:
        """
        Получить флаг сюжета
        
        Args:
            flag: Имя флага
            
        Returns:
            Значение флага
        """
        return self.story_flags.get(flag, False)
        
    def set_variable(self, var: str, value: int) -> None:
        """
        Установить переменную
        
        Args:
            var: Имя переменной
            value: Значение
        """
        self.story_variables[var] = value
        
    def get_variable(self, var: str) -> int:
        """
        Получить переменную
        
        Args:
            var: Имя переменной
            
        Returns:
            Значение переменной
        """
        return self.story_variables.get(var, 0)
        
    def should_show_dialogue(self, dialogue_id: str, current_floor: int) -> bool:
        """
        Проверить, нужно ли показать диалог
        
        Args:
            dialogue_id: ID диалога
            current_floor: Текущий этаж
            
        Returns:
            True если нужно показать
        """
        # Вступление - только один раз
        if dialogue_id == "intro":
            return not self.get_flag("intro_shown")
            
        # Середина - на 10 этаже
        if dialogue_id == "midpoint":
            return current_floor == 10 and not self.get_flag("midpoint_shown")
            
        # Финал - на 20 этаже
        if dialogue_id == "ending":
            return current_floor == 20 and not self.get_flag("ending_shown")
            
        return False


if __name__ == "__main__":
    # Тест менеджера сюжета
    manager = StoryManager()
    
    print("Доступные диалоги:")
    for dialogue_id in manager.dialogues.keys():
        print(f"  - {dialogue_id}")
        
    print("\nТест флагов:")
    manager.set_flag("test", True)
    print(f"  test = {manager.get_flag('test')}")
    
    print("\nТест переменных:")
    manager.set_variable("score", 100)
    print(f"  score = {manager.get_variable('score')}")
