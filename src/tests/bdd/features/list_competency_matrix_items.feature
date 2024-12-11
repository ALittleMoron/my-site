@setup.use_case.list_competency_matrix_use_case
Feature: Список вопросы матрицы компетенций

  Scenario: Успешный вывод списка
    Given Список вопросов в матрице компетенций
      | id | question              | status    | status_changed      | grade.id | subsection.id |
      | 1  | range - это итератор? | published | 2024-12-05 18:00:00 | 1        | 1             |
      | 2  | Что такое декоратор?  | published | 2024-12-05 19:30:00 | 2        | 2             |
    When Получаем список вопросов из матрицы компетенций
    Then Полученный список вопросов матрицы компетенций
      | id | question              | status    | status_changed      | grade.id | subsection.id |
      | 1  | range - это итератор? | published | 2024-12-05 18:00:00 | 1        | 1             |
      | 2  | Что такое декоратор?  | published | 2024-12-05 19:30:00 | 2        | 2             |

  Scenario: В списке выводятся только заполненные данные
    Given Список вопросов в матрице компетенций
      | id | question              | status    | status_changed      | grade.id | subsection.id |
      | 1  | range - это итератор? | published | 2024-12-05 18:00:00 | 1        | 1             |
      | 2  | Что такое декоратор?  | draft     | 2024-12-05 19:30:00 |          |               |
      | 3  | Что такое итератор?   | published | 2024-12-05 19:30:00 | 2        |               |
      | 4  | Что такое генератор?  | published | 2024-12-05 19:30:00 |          | 2             |
    When Получаем список вопросов из матрицы компетенций
    Then Полученный список вопросов матрицы компетенций
      | id | question              | status    | status_changed      | grade.id | subsection.id |
      | 1  | range - это итератор? | published | 2024-12-05 18:00:00 | 1        | 1             |

  Scenario: Выводятся только вопросы, относящиеся к определённому листу
    Given Список подразделов
      | sheet.id | sheet.name | section.id | section.name | subsection.id | subsection.name |
      | 1        | Python     | 1          | Основы       | 1             | ООП             |
    And Список вопросов в матрице компетенций
      | id | question              | status    | status_changed      | grade.id | subsection.id |
      | 1  | Что такое декоратор?  | published | 2024-12-05 19:30:00 | 1        | 1             |
      | 2  | range - это итератор? | published | 2024-12-05 18:00:00 | 2        | 2             |
    When Получаем список вопросов из матрицы компетенций по листу 1
    Then Полученный список вопросов матрицы компетенций
      | id | question             | status    | status_changed      | grade.id | subsection.id |
      | 1  | Что такое декоратор? | published | 2024-12-05 19:30:00 | 1        | 1             |
