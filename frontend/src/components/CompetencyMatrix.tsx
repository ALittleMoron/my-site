
import { useState } from "react";
import { CompetencyBadge } from "./CompetencyBadge";
import { CompetencyTable } from "./CompetencyTable";
import { Input } from "./ui/input";
import { ToggleGroup, ToggleGroupItem } from "./ui/toggle-group";
import { LayoutGrid, LayoutList, Search, X } from "lucide-react";
import { Button } from "./ui/button";

// Translated data
const COMPETENCY_DATA = {
  Python: [
    {
      section: "Основы",
      subsections: [
        {
          name: "Функции",
          content: {
            "Junior": [
              {
                text: "Что такое функция в Python?",
                answer: "Функция - это повторно используемый блок кода, который выполняет определенную задачу. Она может принимать входные данные (параметры) и возвращать выходные данные.",
                resources: ["https://docs.python.org/3/tutorial/controlflow.html#defining-functions"]
              }
            ]
          }
        },
        {
          name: "Типы данных",
          content: {
            "Junior": [
              {
                text: "Объясните основные типы данных в Python",
                answer: "Python имеет несколько встроенных типов данных: int, float, str, bool, list, tuple, dict и set.",
                resources: ["https://docs.python.org/3/library/stdtypes.html"]
              }
            ]
          }
        },
        {
          name: "Аннотации типов",
          content: {
            "Middle": [
              {
                text: "Что такое аннотации типов в Python?",
                answer: "Аннотации типов - это пометки, добавляемые к коду Python, которые указывают ожидаемые типы для аргументов функции и возвращаемых значений.",
                resources: ["https://docs.python.org/3/library/typing.html"]
              }
            ]
          }
        }
      ]
    },
    {
      section: "ООП",
      subsections: [
        {
          name: "Классы",
          content: {
            "Junior": [
              {
                text: "Что такое метод __init__ в Python?",
                answer: "Метод __init__ - это специальный метод в классах Python, который служит конструктором. Он автоматически вызывается при создании нового экземпляра класса.",
                resources: ["https://docs.python.org/3/reference/datamodel.html#object.__init__"]
              }
            ]
          }
        },
        {
          name: "Магические методы",
          content: {
            "Middle": [
              {
                text: "Объясните разницу между __str__ и __repr__",
                answer: "__str__ предназначен для создания читаемого строкового представления объекта, в то время как __repr__ используется для создания однозначного представления объекта, часто для отладки.",
                resources: ["https://docs.python.org/3/reference/datamodel.html#object.__str__"]
              }
            ]
          }
        }
      ]
    },
    {
      section: "Асинхронное программирование",
      subsections: [
        {
          name: "Asyncio",
          content: {
            "Middle": [
              {
                text: "Что такое asyncio в Python?",
                answer: "Asyncio - это библиотека для написания параллельного кода с использованием синтаксиса async/await. Она предоставляет фреймворк для управления корутинами и асинхронными задачами.",
                resources: ["https://docs.python.org/3/library/asyncio.html"]
              }
            ]
          }
        },
        {
          name: "Цикл событий",
          content: {
            "Senior": [
              {
                text: "Реализуйте собственный цикл событий",
                answer: "Создание собственного цикла событий включает расширение базового класса цикла событий и реализацию методов для обработки асинхронных операций.",
                resources: ["https://docs.python.org/3/library/asyncio-eventloop.html"]
              }
            ]
          }
        }
      ]
    },
    {
      section: "Тестирование",
      subsections: [
        {
          name: "Модульные тесты",
          content: {
            "Junior": [
              {
                text: "Что такое unittest в Python?",
                answer: "Unittest - это встроенный фреймворк тестирования Python, который предоставляет инструменты для создания и запуска тестов.",
                resources: ["https://docs.python.org/3/library/unittest.html"]
              }
            ]
          }
        },
        {
          name: "Тестовые фикстуры",
          content: {
            "Middle": [
              {
                text: "Объясните тестовые фикстуры в pytest",
                answer: "Тестовые фикстуры в pytest - это функции, которые обеспечивают фиксированную базу для тестов. Они могут настраивать тестовые данные, создавать подключения или подготавливать ресурсы.",
                resources: ["https://docs.pytest.org/en/stable/fixture.html"]
              }
            ]
          }
        }
      ]
    },
    {
      section: "Логирование",
      subsections: [
        {
          name: "Основы логирования",
          content: {
            "Junior": [
              {
                text: "Как использовать базовое логирование в Python?",
                answer: "Базовое логирование можно выполнять с помощью модуля logging с различными уровнями, такими как DEBUG, INFO, WARNING, ERROR и CRITICAL.",
                resources: ["https://docs.python.org/3/howto/logging.html"]
              }
            ]
          }
        },
        {
          name: "Свой обработчик логирования",
          content: {
            "Senior": [
              {
                text: "Реализуйте свой обработчик логирования",
                answer: "Собственные обработчики логирования можно создать, унаследуя класс Handler и реализуя метод emit для конкретных нужд логирования.",
                resources: ["https://docs.python.org/3/howto/logging-cookbook.html"]
              }
            ]
          }
        }
      ]
    }
  ],
  SQL: [
    {
      section: "Оптимизация запросов",
      subsections: [
        {
          name: "Индексы",
          content: {
            "Junior": [
              {
                text: "Что такое индекс в SQL?",
                answer: "Индекс - это структура данных, которая улучшает скорость операций получения данных из таблиц базы данных.",
                resources: ["https://www.postgresql.org/docs/current/indexes.html"]
              }
            ]
          }
        },
        {
          name: "Планирование запросов",
          content: {
            "Middle": [
              {
                text: "Объясните различные типы индексов",
                answer: "Распространенные типы индексов включают B-tree, Hash, GiST и GIN. Каждый тип оптимизирован для различных шаблонов запросов и типов данных.",
                resources: ["https://www.postgresql.org/docs/current/indexes-types.html"]
              }
            ],
            "Senior": [
              {
                text: "Оптимизируйте сложные объединения с несколькими таблицами",
                answer: "Сложные объединения можно оптимизировать с помощью правильной индексации, порядка объединения и планирования запросов для повышения производительности.",
                resources: ["https://www.postgresql.org/docs/current/performance-tips.html"]
              }
            ]
          }
        }
      ]
    },
    {
      section: "Проектирование базы данных",
      subsections: [
        {
          name: "Нормализация",
          content: {
            "Junior+": [
              {
                text: "Какие нормальные формы существуют в проектировании баз данных?",
                answer: "Нормальные формы - это руководства по нормализации базы данных, которые помогают устранить избыточность данных и обеспечить целостность данных.",
                resources: ["https://www.postgresql.org/docs/current/ddl.html"]
              }
            ]
          }
        },
        {
          name: "Проектирование схемы",
          content: {
            "Senior": [
              {
                text: "Спроектируйте масштабируемую схему базы данных для платформы социальных сетей",
                answer: "Учитывайте такие факторы, как отношения данных, стратегия индексирования, разделение и обработка больших объемов пользовательского контента.",
                resources: ["https://www.postgresql.org/docs/current/ddl-partitioning.html"]
              }
            ]
          }
        }
      ]
    }
  ],
  Architecture: [
    {
      section: "Шаблоны проектирования",
      subsections: [
        {
          name: "Порождающие шаблоны",
          content: {
            "Junior+": [
              {
                text: "Что такое шаблон Одиночка?",
                answer: "Одиночка (Singleton) гарантирует, что класс имеет только один экземпляр и предоставляет глобальную точку доступа к нему.",
                resources: ["https://refactoring.guru/design-patterns/singleton"]
              }
            ]
          }
        },
        {
          name: "Структурные шаблоны",
          content: {
            "Middle": [
              {
                text: "Сравните шаблоны Фабричный метод и Абстрактная фабрика",
                answer: "Фабричный метод создает объекты через наследование, в то время как Абстрактная фабрика создает семейства связанных объектов через композицию.",
                resources: ["https://refactoring.guru/design-patterns/factory-comparison"]
              }
            ]
          }
        },
        {
          name: "Поведенческие шаблоны",
          content: {
            "Senior": [
              {
                text: "Реализуйте шаблон Источник событий",
                answer: "Источник событий (Event Sourcing) хранит состояние бизнес-сущностей как последовательность событий, изменяющих состояние, а не только текущее состояние.",
                resources: ["https://martinfowler.com/eaaDev/EventSourcing.html"]
              }
            ]
          }
        }
      ]
    },
    {
      section: "Проектирование систем",
      subsections: [
        {
          name: "Масштабируемость",
          content: {
            "Middle+": [
              {
                text: "Спроектируйте распределенную систему кэширования",
                answer: "Учитывайте такие аспекты, как инвалидация кэша, согласованность, стратегия распределения и обработка сбоев.",
                resources: ["https://aws.amazon.com/caching/distributed-caching/"]
              }
            ]
          }
        },
        {
          name: "Надежность",
          content: {
            "Senior": [
              {
                text: "Спроектируйте систему уведомлений в реальном времени",
                answer: "Учитывайте масштабируемость, гарантии доставки сообщений, отказоустойчивость и обработку миллионов одновременных подключений.",
                resources: ["https://www.nginx.com/blog/building-a-real-time-notification-system/"]
              }
            ]
          }
        }
      ]
    }
  ],
};

export const CompetencyMatrix = () => {
  const [activeCategory, setActiveCategory] = useState("Python");
  const [searchTerm, setSearchTerm] = useState("");
  const [viewMode, setViewMode] = useState<"list" | "grid">("list");

  const handleCategoryChange = (category: string) => {
    setActiveCategory(category);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
  };

  const handleClearSearch = () => {
    setSearchTerm("");
  };

  const handleViewModeChange = (value: string) => {
    if (value) {
      setViewMode(value as "list" | "grid");
    }
  };

  const filteredData = COMPETENCY_DATA[activeCategory as keyof typeof COMPETENCY_DATA]
    .map(section => {
      const filteredSubsections = section.subsections
        .filter(subsection => {
          // If there's no search term, show everything
          if (!searchTerm) return true;
          
          const searchTermLower = searchTerm.toLowerCase();
          
          // Check if subsection name matches search term
          if (subsection.name.toLowerCase().includes(searchTermLower)) {
            return true;
          }
          
          // Check if any question text matches search term
          for (const [grade, questions] of Object.entries(subsection.content)) {
            if (Array.isArray(questions) && questions.some(q => q.text.toLowerCase().includes(searchTermLower))) {
              return true;
            }
          }
          
          return false;
        });
      
      return {
        section: section.section,
        subsections: filteredSubsections
      };
    })
    .filter(section => section.subsections.length > 0);

  return (
    <div className="min-h-screen bg-matrix-bg p-8 flex flex-col">
      <h1 className="text-3xl font-bold text-gray-100 mb-8">Матрица компетенций</h1>
      
      <div className="bg-matrix-header p-4 rounded-lg border border-matrix-border mb-6">
        <div className="flex flex-wrap gap-4 justify-between items-center">
          <div className="w-full sm:w-auto flex-1 max-w-xs">
            <div className="relative">
              <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                className="pl-8 bg-matrix-bg border-matrix-border text-gray-300 pr-10"
                placeholder="Поиск навыков, вопросов..."
                value={searchTerm}
                onChange={handleSearchChange}
              />
              {searchTerm && (
                <Button
                  variant="ghost"
                  size="icon"
                  className="absolute right-1 top-1/2 transform -translate-y-1/2 h-8 w-8 text-gray-400 hover:text-gray-100"
                  onClick={handleClearSearch}
                  aria-label="Очистить поиск"
                >
                  <X className="h-4 w-4" />
                </Button>
              )}
            </div>
          </div>
          
          <div className="w-auto flex justify-end">
            <ToggleGroup 
              type="single" 
              value={viewMode}
              onValueChange={handleViewModeChange}
              className="border border-matrix-border rounded-md overflow-hidden"
            >
              <ToggleGroupItem 
                value="list" 
                className="h-10 px-3 data-[state=on]:bg-matrix-accent text-gray-300 hover:text-white"
              >
                <LayoutList className="h-4 w-4" />
              </ToggleGroupItem>
              <ToggleGroupItem 
                value="grid" 
                className="h-10 px-3 data-[state=on]:bg-matrix-accent text-gray-300 hover:text-white"
              >
                <LayoutGrid className="h-4 w-4" />
              </ToggleGroupItem>
            </ToggleGroup>
          </div>
        </div>
      </div>
      
      <div className="flex-grow">
        <CompetencyTable 
          data={filteredData} 
          viewMode={viewMode}
        />
      </div>

      <div className="flex flex-wrap gap-3 mt-8 pt-4 border-t border-matrix-border">
        {Object.keys(COMPETENCY_DATA).map((category) => (
          <CompetencyBadge
            key={category}
            name={category}
            isActive={category === activeCategory}
            onClick={() => handleCategoryChange(category)}
          />
        ))}
      </div>
    </div>
  );
};
