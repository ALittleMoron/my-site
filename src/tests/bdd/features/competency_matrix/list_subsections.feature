@setup.use_case.list_subsections_use_case
Feature: Список подразделов к вопросам

  Scenario: Успешный вывод списка
    Given Список подразделов
      | sheet.id | sheet.name | section.id | section.name | subsection.id | subsection.name   |
      | 1        | Python     | 1          | Основы       | 1             | Функции           |
      | 2        | JavaScript | 2          | ООП          | 2             | Магические методы |
    When Получаем список подразделов к вопросам
    Then Полученный список подразделов к вопросам матрицы компетенций
      | sheet.id | sheet.name | section.id | section.name | subsection.id | subsection.name   |
      | 1        | Python     | 1          | Основы       | 1             | Функции           |
      | 2        | JavaScript | 2          | ООП          | 2             | Магические методы |
