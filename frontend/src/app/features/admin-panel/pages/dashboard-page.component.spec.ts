import { DOCUMENT } from '@angular/common';
import { WritableSignal, signal } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { Observable, of, throwError } from 'rxjs';
import { AccountInfo, AuthService } from '../../../core/auth/auth.service';
import { I18nService } from '../../../core/i18n/i18n.service';
import { ApiError } from '../../../core/models/api-error.model';
import { NotificationService } from '../../../core/notifications/notification.service';
import { provideI18nTesting } from '../../../testing/i18n-testing';
import { Calendar } from '../models/calendar.model';
import {
  ModeratorDashboardMatrixStats,
  ModeratorDashboardQueueStats,
} from '../models/moderator-dashboard.model';
import { AdminToolsService } from '../services/admin-tools.service';
import { CalendarService } from '../services/calendar.service';
import { ModeratorDashboardService } from '../services/moderator-dashboard.service';
import { DashboardPageComponent } from './dashboard-page.component';

describe('DashboardPageComponent', () => {
  let fixture: ComponentFixture<DashboardPageComponent>;
  let canManageTeam: WritableSignal<boolean>;
  let currentUser: WritableSignal<AccountInfo | null>;
  let upcomingResponse: Observable<Calendar>;
  let monthResponse: Observable<Calendar>;
  let moderatorQueueResponse: Observable<ModeratorDashboardQueueStats>;
  let moderatorMatrixResponse: Observable<ModeratorDashboardMatrixStats>;
  let getCalendar: jest.Mock;
  let getQueueStats: jest.Mock;
  let getMatrixStats: jest.Mock;
  let toolsService: {
    getCacheStatus: jest.Mock;
    clearCache: jest.Mock;
    startCacheWarm: jest.Mock;
    getCacheWarmOperation: jest.Mock;
    getAuthSessionsStatus: jest.Mock;
    pruneAuthSessions: jest.Mock;
  };

  beforeEach(async () => {
    jest.useFakeTimers();
    jest.setSystemTime(new Date(2026, 6, 31, 12, 30, 0));
    canManageTeam = signal(true);
    currentUser = signal({ username: 'admin', role: 'admin' });
    window.localStorage.clear();
    upcomingResponse = of(populatedCalendar());
    monthResponse = of(monthCalendar());
    moderatorQueueResponse = of(moderatorQueueStats());
    moderatorMatrixResponse = of(moderatorMatrixStats());
    getCalendar = jest.fn((_referenceDate: string, window: string) =>
      window === 'month' ? monthResponse : upcomingResponse,
    );
    getQueueStats = jest.fn(() => moderatorQueueResponse);
    getMatrixStats = jest.fn(() => moderatorMatrixResponse);
    toolsService = {
      getCacheStatus: jest.fn().mockReturnValue(of(cacheStatus())),
      clearCache: jest.fn().mockReturnValue(of(cacheStatus())),
      startCacheWarm: jest.fn(),
      getCacheWarmOperation: jest.fn(),
      getAuthSessionsStatus: jest.fn().mockReturnValue(of(sessionsStatus())),
      pruneAuthSessions: jest.fn(),
    };

    await TestBed.configureTestingModule({
      imports: [DashboardPageComponent],
      providers: [
        provideRouter([]),
        provideI18nTesting(),
        { provide: AuthService, useValue: { canManageTeam, currentUser } },
        { provide: CalendarService, useValue: { getCalendar } },
        {
          provide: ModeratorDashboardService,
          useValue: { getQueueStats, getMatrixStats },
        },
        { provide: AdminToolsService, useValue: toolsService },
        {
          provide: NotificationService,
          useValue: { success: jest.fn(), error: jest.fn() },
        },
      ],
    }).compileComponents();
  });

  afterEach(() => {
    if (fixture && !fixture.componentRef.hostView.destroyed) fixture.destroy();
    jest.useRealTimers();
  });

  function render(): void {
    fixture = TestBed.createComponent(DashboardPageComponent);
    fixture.detectChanges();
  }

  it('renders manager sections as horizontal Resume-style tabs with one visible tabpanel', () => {
    render();

    const tabList = fixture.nativeElement.querySelector(
      '[data-testid="dashboard-tabs"]',
    ) as HTMLElement | null;
    const tabs = Array.from(
      fixture.nativeElement.querySelectorAll('[data-testid^="dashboard-tab-"]'),
    ) as HTMLButtonElement[];
    const panels = Array.from(
      fixture.nativeElement.querySelectorAll('[data-testid^="dashboard-tabpanel-"]'),
    ) as HTMLElement[];

    expect(tabList).not.toBeNull();
    expect(tabList?.getAttribute('role')).toBe('tablist');
    expect(tabList?.classList).toContain('nav-tabs');
    expect(tabList?.classList).toContain('flex-wrap');
    expect(tabs.map((tab) => tab.textContent?.trim())).toEqual([
      'Главная страница',
      'Календарь',
      'Инструменты',
    ]);
    expect(tabs[0].dataset['testid']).toBe('dashboard-tab-home');
    expect(panels[0].dataset['testid']).toBe('dashboard-tabpanel-home');
    expect(
      panels[0].querySelector('[data-testid="dashboard-section-toggle-upcoming-dates"]')
        ?.textContent,
    ).toContain('Памятные даты и дни рождения');
    expect(tabs.map((tab) => tab.getAttribute('aria-selected'))).toEqual([
      'true',
      'false',
      'false',
    ]);
    expect(panels.map((panel) => panel.hidden)).toEqual([false, true, true]);

    tabs[1].click();
    fixture.detectChanges();

    expect(tabs.map((tab) => tab.getAttribute('aria-selected'))).toEqual([
      'false',
      'true',
      'false',
    ]);
    expect(panels.map((panel) => panel.hidden)).toEqual([true, false, true]);
    expect(tabs[1].getAttribute('aria-controls')).toBe(panels[1].id);
    expect(panels[1].getAttribute('aria-labelledby')).toBe(tabs[1].id);
  });

  it('renders moderator sections as their own horizontal tabs', () => {
    canManageTeam.set(false);
    currentUser.set({ username: 'moderator', role: 'moderator' });
    render();

    const tabs = Array.from(
      fixture.nativeElement.querySelectorAll('[data-testid^="dashboard-tab-"]'),
    ) as HTMLButtonElement[];
    const panels = Array.from(
      fixture.nativeElement.querySelectorAll('[data-testid^="dashboard-tabpanel-"]'),
    ) as HTMLElement[];

    expect(tabs.map((tab) => tab.textContent?.trim())).toEqual([
      'Очередь вопросов',
      'Качество матрицы компетенций',
    ]);
    expect(tabs.map((tab) => tab.getAttribute('aria-selected'))).toEqual(['true', 'false']);
    expect(panels.map((panel) => panel.hidden)).toEqual([false, true]);
  });

  it('renders all manager panels with backend summaries and embedded Tools state', () => {
    render();

    expect(getCalendar).toHaveBeenCalledWith('2026-07-31', 'currentAndNextMonths');
    expect(getCalendar).toHaveBeenCalledWith('2026-07-01', 'month');
    expect(getQueueStats).not.toHaveBeenCalled();
    expect(getMatrixStats).not.toHaveBeenCalled();
    const toggles = fixture.nativeElement.querySelectorAll(
      '[data-testid^="dashboard-section-toggle-"]',
    );
    expect(toggles).toHaveLength(3);
    expect(toggles[0].textContent).toContain('Памятная дата: 7');
    expect(toggles[0].textContent).toContain('День рождения: 9');
    expect(toggles[1].textContent).toContain('июль 2026');
    expect(toggles[1].textContent).toContain('Памятная дата: 1');
    expect(toggles[2].textContent).toContain('Кэш и обслуживание сессий');
    expect(toggles[2].textContent).toContain('Включён');
    expect(toggles[2].textContent).toContain('Протухшие: 12');
    expect(fixture.nativeElement.querySelector('app-admin-tools-widget')).not.toBeNull();
  });

  it('renders the upcoming table with links and semantic additional-information lists', () => {
    render();

    const table = fixture.nativeElement.querySelector(
      '[data-testid="dashboard-dates-table"]',
    ) as HTMLTableElement;
    expect(table.closest('.table-responsive')).not.toBeNull();
    expect(table.textContent).toContain('20 июля');
    expect(table.textContent).not.toContain('2020');
    expect(
      table.querySelector('a[href="/admin-panel/knowledge/dates/date-current"]'),
    ).not.toBeNull();
    expect(
      table.querySelector('a[href="/admin-panel/knowledge/people/person-related"]'),
    ).not.toBeNull();
    expect(table.textContent).toContain('Всех / никого');
    expect(
      Array.from(table.querySelectorAll('[data-testid="dashboard-extra-birthday-next"] li')).map(
        (item) => item.textContent?.trim(),
      ),
    ).toEqual(['Следующий месяц', 'Исполняется 26 лет']);
    expect(
      Array.from(table.querySelectorAll('[data-testid="dashboard-extra-date-next"] li')).map(
        (item) => item.textContent?.trim(),
      ),
    ).toEqual(['Следующий месяц', 'Годовщина: 6 лет']);
  });

  it('persists all independent manager panels and restores the username-scoped state', () => {
    render();
    const monthToggle = fixture.nativeElement.querySelector(
      '[data-testid="dashboard-section-toggle-month-calendar"]',
    ) as HTMLButtonElement;
    const toolsToggle = fixture.nativeElement.querySelector(
      '[data-testid="dashboard-section-toggle-tools"]',
    ) as HTMLButtonElement;

    monthToggle.click();
    toolsToggle.click();
    fixture.detectChanges();

    expect(window.localStorage.getItem('adminDashboardSections:v1:admin')).toBe(
      '["month-calendar","tools"]',
    );
    fixture.destroy();
    render();
    expect(
      (
        fixture.nativeElement.querySelector(
          '[data-testid="dashboard-section-toggle-month-calendar"]',
        ) as HTMLButtonElement
      ).getAttribute('aria-expanded'),
    ).toBe('false');
    expect(
      (
        fixture.nativeElement.querySelector(
          '[data-testid="dashboard-section-toggle-tools"]',
        ) as HTMLButtonElement
      ).getAttribute('aria-expanded'),
    ).toBe('false');
  });

  it('isolates persisted section state by username', () => {
    window.localStorage.setItem(
      'adminDashboardSections:v1:admin',
      '["upcoming-dates","unknown-section"]',
    );
    currentUser.set({ username: 'other-admin', role: 'admin' });
    render();

    expect(
      (
        fixture.nativeElement.querySelector(
          '[data-testid="dashboard-section-toggle-upcoming-dates"]',
        ) as HTMLButtonElement
      ).getAttribute('aria-expanded'),
    ).toBe('true');
  });

  it.each(['not-json', '["unknown-section"]'])(
    'defaults all known panels to expanded for invalid persisted state %s',
    (storedValue) => {
      window.localStorage.setItem('adminDashboardSections:v1:admin', storedValue);
      render();

      const toggles = fixture.nativeElement.querySelectorAll(
        '[data-testid^="dashboard-section-toggle-"]',
      );
      expect(
        Array.from(toggles).every((toggle) => toggle.getAttribute('aria-expanded') === 'true'),
      ).toBe(true);
    },
  );

  it('does not require browser storage and keeps panel toggles usable when storage throws', () => {
    const serverDocument = new Proxy(document, {
      get(target, property): unknown {
        if (property === 'defaultView') return null;
        const value: unknown = Reflect.get(target, property, target);
        return typeof value === 'function' ? value.bind(target) : value;
      },
    });
    TestBed.overrideProvider(DOCUMENT, { useValue: serverDocument });
    render();
    const toggle = fixture.nativeElement.querySelector(
      '[data-testid="dashboard-section-toggle-tools"]',
    ) as HTMLButtonElement;
    toggle.click();
    fixture.detectChanges();
    expect(toggle.getAttribute('aria-expanded')).toBe('false');
  });

  it('keeps panel toggles usable when localStorage access throws', () => {
    const getItem = jest.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
      throw new Error('storage unavailable');
    });
    const setItem = jest.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
      throw new Error('storage unavailable');
    });
    try {
      render();
      const toggle = fixture.nativeElement.querySelector(
        '[data-testid="dashboard-section-toggle-month-calendar"]',
      ) as HTMLButtonElement;
      toggle.click();
      fixture.detectChanges();
      expect(toggle.getAttribute('aria-expanded')).toBe('false');
    } finally {
      getItem.mockRestore();
      setItem.mockRestore();
    }
  });

  it('keeps other widgets visible when upcoming dates fail and retries only that widget', () => {
    upcomingResponse = throwError(() => apiError('calendar unavailable'));
    render();

    const upcomingBody = fixture.nativeElement.querySelector(
      '[data-testid="dashboard-section-body-upcoming-dates"]',
    ) as HTMLElement;
    expect(upcomingBody.querySelector('app-error-message')).not.toBeNull();
    expect(
      fixture.nativeElement.querySelector('[data-testid="dashboard-month-grid"]'),
    ).not.toBeNull();
    expect(
      fixture.nativeElement.querySelector('[data-testid="admin-tools-cache-card"]'),
    ).not.toBeNull();

    upcomingResponse = of(emptyCalendar());
    (upcomingBody.querySelector('app-error-message button') as HTMLButtonElement).click();
    fixture.detectChanges();
    expect(upcomingBody.querySelector('app-empty-state')).not.toBeNull();
    expect(toolsService.getCacheStatus).toHaveBeenCalledTimes(1);
  });

  it('keeps the matrix panel usable when the moderator queue request fails', () => {
    canManageTeam.set(false);
    currentUser.set({ username: 'moderator', role: 'moderator' });
    moderatorQueueResponse = throwError(() => apiError('queue unavailable'));
    render();

    expect(getCalendar).not.toHaveBeenCalled();
    expect(toolsService.getCacheStatus).not.toHaveBeenCalled();
    const toggles = fixture.nativeElement.querySelectorAll(
      '[data-testid^="dashboard-section-toggle-"]',
    );
    expect(toggles).toHaveLength(2);
    expect(toggles[0].textContent).toContain('Очередь вопросов');
    expect(toggles[1].textContent).toContain('Качество матрицы компетенций');
    const queueBody = fixture.nativeElement.querySelector(
      '[data-testid="dashboard-section-body-moderator-question-queue"]',
    ) as HTMLElement;
    const matrixBody = fixture.nativeElement.querySelector(
      '[data-testid="dashboard-section-body-moderator-matrix-quality"]',
    ) as HTMLElement;
    expect(queueBody.querySelector('app-error-message')).not.toBeNull();
    expect(matrixBody.querySelector('app-error-message')).toBeNull();
    expect(matrixBody.textContent).toContain('Черновики с пропусками');

    moderatorQueueResponse = of(moderatorQueueStats());
    (queueBody.querySelector('app-error-message button') as HTMLButtonElement).click();
    fixture.detectChanges();

    expect(queueBody.querySelector('app-error-message')).toBeNull();
    expect(getQueueStats).toHaveBeenCalledTimes(2);
    expect(getMatrixStats).toHaveBeenCalledTimes(1);
  });

  it('keeps the queue panel usable when the moderator matrix request fails', () => {
    canManageTeam.set(false);
    currentUser.set({ username: 'moderator', role: 'moderator' });
    moderatorMatrixResponse = throwError(() => apiError('matrix unavailable'));
    render();

    const queueBody = fixture.nativeElement.querySelector(
      '[data-testid="dashboard-section-body-moderator-question-queue"]',
    ) as HTMLElement;
    const matrixBody = fixture.nativeElement.querySelector(
      '[data-testid="dashboard-section-body-moderator-matrix-quality"]',
    ) as HTMLElement;
    expect(queueBody.querySelector('app-error-message')).toBeNull();
    expect(queueBody.textContent).toContain('Всего в очереди');
    expect(matrixBody.querySelector('app-error-message')).not.toBeNull();

    moderatorMatrixResponse = of(moderatorMatrixStats());
    (matrixBody.querySelector('app-error-message button') as HTMLButtonElement).click();
    fixture.detectChanges();

    expect(matrixBody.querySelector('app-error-message')).toBeNull();
    expect(getMatrixStats).toHaveBeenCalledTimes(2);
    expect(getQueueStats).toHaveBeenCalledTimes(1);
  });

  it('renders moderator statistics and links without manager-only widgets', () => {
    canManageTeam.set(false);
    currentUser.set({ username: 'moderator', role: 'moderator' });
    render();

    expect(getCalendar).not.toHaveBeenCalled();
    expect(getQueueStats).toHaveBeenCalledTimes(1);
    expect(getMatrixStats).toHaveBeenCalledWith('ru');
    const view = fixture.nativeElement.querySelector(
      '[data-testid="dashboard-moderator-view"]',
    ) as HTMLElement;
    expect(view.textContent).toContain('Всего в очереди');
    expect(view.textContent).toContain('Черновики с пропусками');
    expect(
      view.querySelector('a[href="/admin-panel/matrix-question-queue?availability=available"]'),
    ).not.toBeNull();
    expect(
      view.querySelector(
        'a[href="/admin-panel/matrix-questions?publishStatus=Draft&hasMissingFields=true"]',
      ),
    ).not.toBeNull();
    expect(view.querySelector('app-admin-tools-widget')).toBeNull();
    expect(view.querySelector('app-month-calendar-widget')).toBeNull();
  });

  it('refreshes all manager widgets and uses the current browser-local date for upcoming dates', () => {
    render();
    jest.setSystemTime(new Date(2026, 7, 1, 8, 0, 0));

    (
      fixture.nativeElement.querySelector('[data-testid="dashboard-refresh"]') as HTMLButtonElement
    ).click();
    fixture.detectChanges();

    expect(getCalendar).toHaveBeenCalledWith('2026-08-01', 'currentAndNextMonths');
    expect(getCalendar).toHaveBeenCalledWith('2026-07-01', 'month');
    expect(toolsService.getCacheStatus).toHaveBeenCalledTimes(2);
    expect(toolsService.getAuthSessionsStatus).toHaveBeenCalledTimes(2);
  });

  it('uses Russian and English Intl plural categories for ages and anniversaries', () => {
    upcomingResponse = of(pluralCalendar());
    render();
    const i18n = TestBed.inject(I18nService);

    expect(fixture.componentInstance.additionalInfoItems(pluralCalendar().entries[0])).toEqual([
      'Исполняется 1 год',
    ]);
    expect(fixture.componentInstance.additionalInfoItems(pluralCalendar().entries[1])).toEqual([
      'Исполняется 2 года',
    ]);
    expect(fixture.componentInstance.additionalInfoItems(pluralCalendar().entries[2])).toEqual([
      'Исполняется 5 лет',
    ]);
    expect(fixture.componentInstance.additionalInfoItems(pluralCalendar().entries[3])).toEqual([
      'Годовщина: 1 год',
    ]);

    i18n.switchLanguage('en').subscribe();
    fixture.detectChanges();

    expect(fixture.componentInstance.additionalInfoItems(pluralCalendar().entries[0])).toEqual([
      'Turns 1 year old',
    ]);
    expect(fixture.componentInstance.additionalInfoItems(pluralCalendar().entries[1])).toEqual([
      'Turns 2 years old',
    ]);
    expect(fixture.componentInstance.additionalInfoItems(pluralCalendar().entries[3])).toEqual([
      'Anniversary: 1 year',
    ]);
    expect(fixture.nativeElement.textContent).toContain('July 20');
  });
});

function moderatorQueueStats(): ModeratorDashboardQueueStats {
  return { total: 3, available: 1, claimed: 2 };
}

function moderatorMatrixStats(): ModeratorDashboardMatrixStats {
  return { draft: 8, missingDraft: 4, dangerousPublished: 2 };
}

function populatedCalendar(): Calendar {
  return {
    referenceDate: '2026-07-31',
    window: 'currentAndNextMonths',
    summary: { memorableDateCount: 7, birthdayCount: 9 },
    entries: [
      {
        id: 'date-current',
        kind: 'memorableDate',
        displayName: 'Текущая дата',
        annualDate: { day: 20, month: 7, year: 2020 },
        period: 'currentMonth',
        occurrenceYear: 2026,
        relatedPeople: [{ id: 'person-related', displayName: 'Анна' }],
      },
      {
        id: 'birthday-current',
        kind: 'birthday',
        displayName: 'Текущий день рождения',
        annualDate: { day: 20, month: 7, year: null },
        period: 'currentMonth',
        occurrenceYear: 2026,
        relatedPeople: [],
      },
      {
        id: 'date-next',
        kind: 'memorableDate',
        displayName: 'Следующая дата',
        annualDate: { day: 2, month: 8, year: 2020 },
        period: 'nextMonth',
        occurrenceYear: 2026,
        relatedPeople: [],
      },
      {
        id: 'birthday-next',
        kind: 'birthday',
        displayName: 'Следующий день рождения',
        annualDate: { day: 2, month: 8, year: 2000 },
        period: 'nextMonth',
        occurrenceYear: 2026,
        relatedPeople: [],
      },
    ],
  };
}

function monthCalendar(): Calendar {
  return {
    referenceDate: '2026-07-01',
    window: 'month',
    summary: { memorableDateCount: 1, birthdayCount: 1 },
    entries: [],
  };
}

function emptyCalendar(): Calendar {
  return {
    referenceDate: '2026-07-31',
    window: 'currentAndNextMonths',
    summary: { memorableDateCount: 0, birthdayCount: 0 },
    entries: [],
  };
}

function pluralCalendar(): Calendar {
  return {
    ...emptyCalendar(),
    summary: { memorableDateCount: 1, birthdayCount: 3 },
    entries: [
      birthday('one', 2025),
      birthday('few', 2024),
      birthday('many', 2021),
      {
        id: 'anniversary-one',
        kind: 'memorableDate',
        displayName: 'Годовщина',
        annualDate: { day: 20, month: 7, year: 2025 },
        period: 'currentMonth',
        occurrenceYear: 2026,
        relatedPeople: [],
      },
    ],
  };
}

function birthday(id: string, year: number): Calendar['entries'][number] {
  return {
    id,
    kind: 'birthday',
    displayName: id,
    annualDate: { day: 20, month: 7, year },
    period: 'currentMonth',
    occurrenceYear: 2026,
    relatedPeople: [],
  };
}

function cacheStatus(): object {
  return {
    enabled: true,
    configuredTtlSeconds: 86400,
    scheduledWarmIntervalSeconds: 3600,
    domains: [],
    lastManualWarmOperation: null,
  };
}

function sessionsStatus(): object {
  return {
    expiredCount: 12,
    expiringSoonCount: 4,
    expiringSoonDays: 7,
    scheduledPruneIntervalSeconds: 3600,
  };
}

function apiError(message: string): ApiError {
  return {
    code: 'dashboard_error',
    type: 'server_error',
    message,
    location: null,
    attr: null,
  };
}
