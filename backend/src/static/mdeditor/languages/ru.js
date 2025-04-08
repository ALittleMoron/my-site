(function(){
    var factory = function (exports) {
        var lang = {
            name : "ru",
            description : "Онлайн редактор языка Markdown с открытым исходным кодом.",
            tocTitle    : "Оглавление",
            toolbar : {
                undo             : "Назад (Ctrl + Z)",
                redo             : "Вперёд (Ctrl + Y)",
                bold             : "Выделить жирным",
                del              : "Зачеркнуть",
                italic           : "Выделить курсивом",
                quote            : "Блок цитаты",
                ucwords          : "Преобразовать первые буквы выбранных слов в заглавные (не работает с русским языком)",
                uppercase        : "Преобразовать выбранный текст в заглавный",
                lowercase        : "Преобразовать выбранный текст в строчный",
                h1               : "Заголовок 1 уровня",
                h2               : "Заголовок 2 уровня",
                h3               : "Заголовок 3 уровня",
                h4               : "Заголовок 4 уровня",
                h5               : "Заголовок 5 уровня",
                h6               : "Заголовок 6 уровня",
                "list-ul"        : "Неупорядоченный список",
                "list-ol"        : "Упорядоченный список",
                hr               : "Горизонтальная линейка",
                link             : "Ссылка",
                "reference-link" : "Ссылка для справки",
                image            : "Изображение",
                code             : "Встроенный код",
                "preformatted-text" : "Предварительно отформатированный текст / Блок кода (отступ табуляции)",
                "code-block"     : "Блок кода (многоязычный)",
                table            : "Таблицы",
                datetime         : "Дата и время",
                emoji            : "Эмордзи",
                "html-entities"  : "HTML-сущности",
                pagebreak        : "Разрыв страницы",
                watch            : "Режим предпросмотра (Вкл.)",
                unwatch          : "Режим предпросмотра (Выкл.)",
                preview          : "HTML-превью",
                fullscreen       : "Полноэкранный режим (ESC для выхода)",
                clear            : "Очистка",
                search           : "Поиск",
                help             : "Справка",
                info             : "About " + exports.title
            },
            buttons : {
                enter  : "Ввести",
                cancel : "Отменить",
                close  : "Закрыть"
            },
            dialog : {
                link : {
                    title    : "Ссылка",
                    url      : "Адрес",
                    urlTitle : "Заголовок ссылки",
                    urlEmpty : "Ошибка: заполните адрес ссылки."
                },
                referenceLink : {
                    title    : "Ссылка для справки",
                    name     : "Название",
                    url      : "Адрес",
                    urlId    : "Идентификатор",
                    urlTitle : "Заголовок ссылки",
                    nameEmpty: "Ошибка: название не может быть пустым.",
                    idEmpty  : "Ошибка: заполните идентификатор ссылки.",
                    urlEmpty : "Ошибка: заполните адрес ссылки."
                },
                image : {
                    title    : "Изображение",
                    url      : "Адрес",
                    link     : "Ссылка",
                    alt      : "Текст при наведении",
                    uploadButton     : "Загрузить",
                    imageURLEmpty    : "Ошибка: адрес картинки не может быть пустым.",
                    uploadFileEmpty  : "Ошибка: загруженный файл не может быть пустым!",
                    formatNotAllowed : "Ошибка: разрешено загружать только изображения следующего формата:"
                },
                preformattedText : {
                    title             : "Предварительно отформатированный текст / Код",
                    emptyAlert        : "Ошибка: заполните предварительно отформатированный текст или содержимое кода.",
                    placeholder       : "Добавьте код...."
                },
                codeBlock : {
                    title             : "Блок кода",
                    selectLabel       : "Языки: ",
                    selectDefaultText : "Выберите язык программирования...",
                    otherLanguage     : "Другие языки",
                    unselectedLanguageAlert : "Ошибка: выберите язык программирования.",
                    codeEmptyAlert    : "Ошибка: заполните содержимое кода.",
                    placeholder       : "Добавьте код...."
                },
                htmlEntities : {
                    title : "HTML-сущности"
                },
                help : {
                    title : "Справка"
                }
            }
        };

        exports.defaults.lang = lang;
    };

    // CommonJS/Node.js
    if (typeof require === "function" && typeof exports === "object" && typeof module === "object")
    {
        module.exports = factory;
    }
    else if (typeof define === "function")  // AMD/CMD/Sea.js
    {
        if (define.amd) { // for Require.js

            define(["editormd"], function(editormd) {
                factory(editormd);
            });

        } else { // for Sea.js
            define(function(require) {
                var editormd = require("../editormd");
                factory(editormd);
            });
        }
    }
    else
    {
        factory(window.editormd);
    }

})();
