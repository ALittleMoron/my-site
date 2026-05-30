import { Provider, signal } from '@angular/core';
import { of, throwError } from 'rxjs';
import { I18nParams, LanguageCode } from '../core/i18n/i18n.model';
import { I18nService } from '../core/i18n/i18n.service';

const I18N_TEST_MESSAGES: Record<string, string> = {
  'app.siteName': 'Мой сайт',
  'shared.back': 'Назад',
  'shared.next': 'Вперёд',
  'shared.edit': 'Редактировать',
  'shared.delete': 'Удалить',
  'shared.publish': 'Опубликовать',
  'shared.unpublish': 'Снять с публикации',
  'shared.update': 'Обновить',
  'shared.draft': 'Черновик',
  'about.contact.sendError': 'Не удалось отправить заявку.',
  'about.contact.successTitle': 'Заявка отправлена!',
  'about.contact.successText': 'Я свяжусь с вами в ближайшее время.',
  'about.contact.sent': 'Заявка отправлена.',
  'matrix.title': 'Матрица компетенций',
  'matrix.detail.question': 'Вопрос:',
  'matrix.detail.answer': 'Ответ:',
  'matrix.detail.expectedAnswer': 'Ответ, который ожидается на собеседовании:',
  'matrix.detail.resources': 'Внешние ресурсы:',
  'matrix.filter.searchPlaceholder': 'Поиск навыков и вопросов',
  'matrix.filter.clear': 'Очистить',
  'matrix.filter.clearSearch': 'Очистить поиск',
  'matrix.filter.onlyPublished': 'Только опубликованные',
  'matrix.filter.layout': 'Переключение вида',
  'matrix.filter.listView': 'Список',
  'matrix.filter.gridView': 'Таблица',
  'matrix.grid.section': 'Раздел',
  'matrix.grid.subsection': 'Подраздел',
  'matrix.notify.published': 'Вопрос опубликован.',
  'matrix.notify.publishError': 'Не удалось опубликовать вопрос.',
  'matrix.notify.unpublished': 'Вопрос снят с публикации.',
  'matrix.notify.unpublishError': 'Не удалось снять вопрос с публикации.',
  'matrix.notify.deleted': 'Вопрос удалён.',
  'matrix.notify.deleteError': 'Не удалось удалить вопрос.',
  'notes.views': '{count} просмотров',
  'notes.stats.from': 'С',
  'notes.stats.to': 'По',
  'notes.stats.views': 'Просмотры: {count}',
  'notes.stats.engaged': 'Вовлечённые: {count}',
  'notes.stats.reactions': 'Реакции: {count}',
  'notes.stats.note': 'Заметка',
  'notes.stats.viewsColumn': 'Просмотры',
  'notes.stats.engagedColumn': 'Вовлечённые',
  'enum.grade.Junior': 'Junior',
  'enum.grade.JuniorPlus': 'Junior+',
  'enum.grade.Middle': 'Middle',
  'enum.grade.MiddlePlus': 'Middle+',
  'enum.grade.Senior': 'Senior',
  'enum.noteReaction.heart': 'Понравилось',
  'enum.noteReaction.fire': 'Хочу ещё',
  'enum.noteReaction.thinking': 'Заставило подумать',
  'enum.noteReaction.neutral': 'Нормально',
  'enum.noteReaction.poop': 'Не зашло',
};

export function provideI18nTesting(messages: Record<string, string> = {}): Provider {
  return {
    provide: I18nService,
    useValue: createI18nTestingValue(messages),
  };
}

export function createI18nTestingValue(
  messages: Record<string, string> = {},
): Partial<I18nService> {
  const mergedMessages = { ...I18N_TEST_MESSAGES, ...messages };
  const language = signal<LanguageCode | null>('ru');
  const languages = signal([
    { code: 'ru' as const, label: 'Русский' },
    { code: 'en' as const, label: 'English' },
  ]);
  const startupError = signal(false);

  return {
    language,
    languages,
    startupError,
    initialize: () => of(void 0),
    retryStartup: () => of(void 0),
    switchLanguage: (nextLanguage: LanguageCode) => {
      if (!languages().some((item) => item.code === nextLanguage)) {
        return throwError(() => new Error(`Unsupported language: ${nextLanguage}`));
      }
      language.set(nextLanguage);
      return of(void 0);
    },
    translate: (key: string, params?: I18nParams) =>
      interpolate(mergedMessages[key] ?? key, params),
    enumGradeKey: (grade: string) => `enum.grade.${grade.replace('+', 'Plus')}`,
    dateLocale: () => 'ru-RU',
  };
}

function interpolate(template: string, params?: I18nParams): string {
  if (!params) return template;
  return Object.entries(params).reduce(
    (text, [name, value]) => text.replaceAll(`{${name}}`, String(value)),
    template,
  );
}
