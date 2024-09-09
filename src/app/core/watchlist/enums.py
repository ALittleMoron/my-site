from enum import StrEnum


class WatchListElementStatus(StrEnum):
    WATCHED = "WATCHED"  # Просмотрено
    ABANDONED = "ABANDONED"  # Брошено
    POSTPONED = "POSTPONED"  # Отложено
    SCHEDULED = "SCHEDULED"  # Запланировано
    REVIEWING = "REVIEWING"  # Пересматриваю


class WatchListElementKind(StrEnum):
    FILM = "FILM"  # Фильм
    SERIES = "SERIES"  # Сериал
    MINI_SERIES = "MINI_SERIES"  # Мини-сериал
    SPECIAL = "SPECIAL"  # Специальный выпуск сериала
    SHORT_FILM = "SHORT_FILM"  # Короткометражка


class WatchListElementType(StrEnum):
    REGULAR = "REGULAR"  # обычные фильмы, сериалы
    ANIME = "ANIME"  # Японские мультики
