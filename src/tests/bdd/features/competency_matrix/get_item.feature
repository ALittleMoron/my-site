@setup.use_case.get_competency_matrix_use_case
Feature: Детальная информация вопроса в матрице компетенций

  Scenario: Получение - успешное
    Given Список подразделов
      | sheet.id | sheet.name | section.id | section.name | subsection.id | subsection.name   |
      | 1        | Python     | 1          | Основы       | 1             | Функции           |
      | 1        | Python     | 2          | ООП          | 2             | магические методы |
    And Список компетенций
      | grade.id | grade.name |
      | 1        | Junior     |
      | 2        | Middle     |
    And Полный список вопросов в матрице компетенций
      | id | question              | answer  | interview_expected_answer | status    | status_changed      | grade.id | grade.name | sheet.id | sheet.name | section.id | section.name | subsection.id | subsection.name   |
      | 1  | Что такое декоратор?  | Не знаю | Знаю                      | published | 2024-12-05 19:30:00 | 1        | Junior     | 1        | Python     | 1          | Основы       | 1             | Функции           |
      | 2  | range - это итератор? | Нет     | Нет                       | published | 2024-12-05 18:00:00 | 2        | Middle     | 1        | Python     | 2          | ООП          | 2             | магические методы |
    And Список дополнительных ресурсов у вопроса 1
      | resource.id | resource.name            | resource.url | resource.context |
      | 1           | Книга "Незнайка на луне" |              | хорошая книга    |
    When Получаем вопроса 1 из матрицы компетенций
    Then Полученный вопрос из матрицы компетенций
      | field                     | value                |
      | id                        | 1                    |
      | question                  | Что такое декоратор? |
      | answer                    | Не знаю              |
      | interview_expected_answer | Знаю                 |
      | status                    | published            |
      | status_changed            | 2024-12-05 19:30:00  |
      | grade.id                  | 1                    |
      | grade.name                | Junior               |
      | subsection.id             | 1                    |
      | subsection.name           | Функции              |
      | section.id                | 1                    |
      | section.name              | Основы               |
      | sheet.id                  | 1                    |
      | sheet.name                | Python               |
    And Полученный список дополнительных ресурсов к вопросу 1
      | resource.id | resource.name            | resource.url | resource.context |
      | 1           | Книга "Незнайка на луне" |              | хорошая книга    |
