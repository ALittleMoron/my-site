@setup.use_case.list_sheets_use_case
Feature: Список листов с вопросами

  Scenario: Успешный вывод списка
    Given Список листов с вопросами
      | sheet.id | sheet.name |
      | 1        | Python     |
      | 2        | JavaScript |
    When Получаем список листов с вопросами
    Then Полученный список листов с вопросами матрицы компетенций
      | sheet.id | sheet.name |
      | 1        | Python     |
      | 2        | JavaScript |
