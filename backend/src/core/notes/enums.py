from core.enums import LabeledStrEnum


class NoteReactionKind(LabeledStrEnum):
    HEART = "heart", "Понравилось"
    FIRE = "fire", "Хочу ещё"
    THINKING = "thinking", "Заставило подумать"
    NEUTRAL = "neutral", "Нормально"
    POOP = "poop", "Не зашло"


class NoteViewSourceCategory(LabeledStrEnum):
    DIRECT = "Direct", "Прямой"
    INTERNAL = "Internal", "Внутренний"
    SEARCH = "Search", "Поиск"
    SOCIAL = "Social", "Соцсети"
    EXTERNAL = "External", "Внешний"
    UNKNOWN = "Unknown", "Неизвестный"
