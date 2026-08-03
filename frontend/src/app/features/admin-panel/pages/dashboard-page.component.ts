import { DOCUMENT } from '@angular/common';
import {
  ChangeDetectionStrategy,
  Component,
  DestroyRef,
  OnInit,
  ViewChild,
  computed,
  effect,
  inject,
  signal,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { AuthService } from '../../../core/auth/auth.service';
import { I18nService } from '../../../core/i18n/i18n.service';
import { TranslatePipe } from '../../../core/i18n/translate.pipe';
import { ApiError } from '../../../core/models/api-error.model';
import { EmptyStateComponent } from '../../../shared/ui/empty-state/empty-state.component';
import { ErrorMessageComponent } from '../../../shared/ui/error-message/error-message.component';
import { LoadingSpinnerComponent } from '../../../shared/ui/loading-spinner/loading-spinner.component';
import { DashboardFoldableSectionComponent } from '../components/dashboard-foldable-section/dashboard-foldable-section.component';
import { AdminToolsWidgetComponent } from '../components/admin-tools-widget/admin-tools-widget.component';
import { MonthCalendarWidgetComponent } from '../components/month-calendar-widget/month-calendar-widget.component';
import { formatAnnualDate } from '../knowledge/shared/annual-date';
import { Calendar, CalendarEntry } from '../models/calendar.model';
import {
  ModeratorDashboardMatrixStats,
  ModeratorDashboardQueueStats,
} from '../models/moderator-dashboard.model';
import { CalendarService } from '../services/calendar.service';
import { ModeratorDashboardService } from '../services/moderator-dashboard.service';

type DashboardSectionKey =
  | 'upcoming-dates'
  | 'month-calendar'
  | 'tools'
  | 'moderator-question-queue'
  | 'moderator-matrix-quality';

type DashboardTabKey =
  'home' | 'month-calendar' | 'tools' | 'moderator-question-queue' | 'moderator-matrix-quality';

interface DashboardTabDefinition {
  key: DashboardTabKey;
  labelKey: string;
}

const MANAGER_DASHBOARD_TABS: readonly DashboardTabDefinition[] = [
  { key: 'home', labelKey: 'dashboard.home.title' },
  { key: 'month-calendar', labelKey: 'dashboard.calendar.title' },
  { key: 'tools', labelKey: 'dashboard.tools.title' },
];

const MODERATOR_DASHBOARD_TABS: readonly DashboardTabDefinition[] = [
  { key: 'moderator-question-queue', labelKey: 'dashboard.moderator.queue.title' },
  { key: 'moderator-matrix-quality', labelKey: 'dashboard.moderator.matrix.title' },
];

const MANAGER_DASHBOARD_SECTIONS: readonly DashboardSectionKey[] = [
  'upcoming-dates',
  'month-calendar',
  'tools',
];

const MODERATOR_DASHBOARD_SECTIONS: readonly DashboardSectionKey[] = [
  'moderator-question-queue',
  'moderator-matrix-quality',
];

@Component({
  selector: 'app-dashboard-page',
  standalone: true,
  imports: [
    RouterLink,
    TranslatePipe,
    EmptyStateComponent,
    ErrorMessageComponent,
    LoadingSpinnerComponent,
    DashboardFoldableSectionComponent,
    MonthCalendarWidgetComponent,
    AdminToolsWidgetComponent,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './dashboard-page.component.html',
  styleUrl: './dashboard-page.component.scss',
})
export class DashboardPageComponent implements OnInit {
  private readonly auth = inject(AuthService);
  private readonly calendarService = inject(CalendarService);
  private readonly moderatorDashboardService = inject(ModeratorDashboardService);
  private readonly i18n = inject(I18nService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly document = inject(DOCUMENT);
  private upcomingLoadGeneration = 0;
  private moderatorQueueLoadGeneration = 0;
  private moderatorMatrixLoadGeneration = 0;

  @ViewChild(MonthCalendarWidgetComponent)
  private monthCalendarWidget: MonthCalendarWidgetComponent | undefined;
  @ViewChild(AdminToolsWidgetComponent)
  private adminToolsWidget: AdminToolsWidgetComponent | undefined;

  readonly canManageTeam = this.auth.canManageTeam;
  readonly upcomingCalendar = signal<Calendar | null>(null);
  readonly moderatorQueueStats = signal<ModeratorDashboardQueueStats | null>(null);
  readonly moderatorMatrixStats = signal<ModeratorDashboardMatrixStats | null>(null);
  readonly upcomingLoading = signal(false);
  readonly upcomingError = signal<ApiError | null>(null);
  readonly moderatorQueueLoading = signal(false);
  readonly moderatorQueueError = signal<ApiError | null>(null);
  readonly moderatorMatrixLoading = signal(false);
  readonly moderatorMatrixError = signal<ApiError | null>(null);
  readonly monthCalendarSummary = signal<string | null>(null);
  readonly toolsStatusSummary = signal<string | null>(null);
  readonly activeTab = signal<DashboardTabKey>('home');
  readonly tabs = computed<readonly DashboardTabDefinition[]>(() =>
    this.canManageTeam() ? MANAGER_DASHBOARD_TABS : MODERATOR_DASHBOARD_TABS,
  );
  readonly collapsedSectionKeys = signal<ReadonlySet<string>>(new Set<string>());
  readonly knownSectionKeys = computed<readonly DashboardSectionKey[]>(() =>
    this.canManageTeam() ? MANAGER_DASHBOARD_SECTIONS : MODERATOR_DASHBOARD_SECTIONS,
  );
  readonly datesSummary = computed(() => {
    this.i18n.language();
    const summary = this.upcomingCalendar()?.summary;
    return `${this.i18n.translate('dashboard.dates.type.memorableDate')}: ${summary?.memorableDateCount ?? 0} · ${this.i18n.translate('dashboard.dates.type.birthday')}: ${summary?.birthdayCount ?? 0}`;
  });
  readonly calendarPanelSummary = computed(() => {
    this.i18n.language();
    return this.monthCalendarSummary() ?? this.i18n.translate('dashboard.calendar.loadingSummary');
  });
  readonly toolsPanelSummary = computed(() => {
    this.i18n.language();
    return this.toolsStatusSummary() ?? this.i18n.translate('dashboard.tools.summary');
  });
  readonly moderatorQueueSummary = computed(() => {
    this.i18n.language();
    const queue = this.moderatorQueueStats();
    return `${this.i18n.translate('dashboard.moderator.queue.total')}: ${queue?.total ?? 0} · ${this.i18n.translate('dashboard.moderator.queue.available')}: ${queue?.available ?? 0} · ${this.i18n.translate('dashboard.moderator.queue.claimed')}: ${queue?.claimed ?? 0}`;
  });
  readonly moderatorMatrixSummary = computed(() => {
    this.i18n.language();
    const matrix = this.moderatorMatrixStats();
    return `${this.i18n.translate('dashboard.moderator.matrix.draft')}: ${matrix?.draft ?? 0} · ${this.i18n.translate('dashboard.moderator.matrix.missingDraft')}: ${matrix?.missingDraft ?? 0} · ${this.i18n.translate('dashboard.moderator.matrix.dangerousPublished')}: ${matrix?.dangerousPublished ?? 0}`;
  });

  constructor() {
    effect(() => {
      const username = this.auth.currentUser()?.username;
      const tabs = this.tabs();
      const knownTabKeys = new Set<DashboardTabKey>(tabs.map((tab) => tab.key));
      const firstTab = tabs[0];
      if (firstTab !== undefined && !knownTabKeys.has(this.activeTab())) {
        this.activeTab.set(firstTab.key);
      }
      this.collapsedSectionKeys.set(
        this.readCollapsedSectionKeys(username, new Set(this.knownSectionKeys())),
      );
    });
  }

  ngOnInit(): void {
    if (this.canManageTeam()) {
      this.loadUpcomingDates();
    } else {
      this.loadModeratorQueue();
      this.loadModeratorMatrix();
    }
  }

  loadDashboard(): void {
    if (this.canManageTeam()) {
      this.loadUpcomingDates();
      this.monthCalendarWidget?.loadSelectedMonth();
      this.adminToolsWidget?.loadCacheStatus();
      this.adminToolsWidget?.loadSessionsStatus();
      return;
    }
    this.loadModeratorQueue();
    this.loadModeratorMatrix();
  }

  loadUpcomingDates(): void {
    const generation = ++this.upcomingLoadGeneration;
    this.upcomingLoading.set(true);
    this.upcomingError.set(null);
    this.calendarService
      .getCalendar(browserLocalDate(new Date()), 'currentAndNextMonths')
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (calendar) => {
          if (generation !== this.upcomingLoadGeneration) return;
          this.upcomingCalendar.set(calendar);
          this.upcomingLoading.set(false);
        },
        error: (error: ApiError) => {
          if (generation !== this.upcomingLoadGeneration) return;
          this.upcomingError.set(error);
          this.upcomingLoading.set(false);
        },
      });
  }

  loadModeratorQueue(): void {
    const generation = ++this.moderatorQueueLoadGeneration;
    this.moderatorQueueLoading.set(true);
    this.moderatorQueueError.set(null);
    this.moderatorDashboardService
      .getQueueStats()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (queue) => {
          if (generation !== this.moderatorQueueLoadGeneration) return;
          this.moderatorQueueStats.set(queue);
          this.moderatorQueueLoading.set(false);
        },
        error: (error: ApiError) => {
          if (generation !== this.moderatorQueueLoadGeneration) return;
          this.moderatorQueueError.set(error);
          this.moderatorQueueLoading.set(false);
        },
      });
  }

  loadModeratorMatrix(): void {
    const generation = ++this.moderatorMatrixLoadGeneration;
    this.moderatorMatrixLoading.set(true);
    this.moderatorMatrixError.set(null);
    this.moderatorDashboardService
      .getMatrixStats(this.i18n.language()!)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (matrix) => {
          if (generation !== this.moderatorMatrixLoadGeneration) return;
          this.moderatorMatrixStats.set(matrix);
          this.moderatorMatrixLoading.set(false);
        },
        error: (error: ApiError) => {
          if (generation !== this.moderatorMatrixLoadGeneration) return;
          this.moderatorMatrixError.set(error);
          this.moderatorMatrixLoading.set(false);
        },
      });
  }

  isSectionExpanded(sectionKey: DashboardSectionKey): boolean {
    return !this.collapsedSectionKeys().has(sectionKey);
  }

  setSectionExpanded(sectionKey: DashboardSectionKey, expanded: boolean): void {
    if (!this.knownSectionKeys().includes(sectionKey)) return;
    this.collapsedSectionKeys.update((current) => {
      const next = new Set(current);
      if (expanded) {
        next.delete(sectionKey);
      } else {
        next.add(sectionKey);
      }
      return next;
    });
    this.writeCollapsedSectionKeys(this.auth.currentUser()?.username);
  }

  setActiveTab(tabKey: DashboardTabKey): void {
    if (!this.tabs().some((tab) => tab.key === tabKey)) return;
    this.activeTab.set(tabKey);
  }

  tabId(tabKey: DashboardTabKey): string {
    return `dashboard-tab-${tabKey}`;
  }

  tabPanelId(tabKey: DashboardTabKey): string {
    return `dashboard-tabpanel-${tabKey}`;
  }

  annualDateLabel(entry: CalendarEntry): string {
    return formatAnnualDate(
      { day: entry.annualDate.day, month: entry.annualDate.month, year: null },
      this.i18n.dateLocale(),
    );
  }

  entryRoute(entry: CalendarEntry): readonly string[] {
    if (entry.kind === 'memorableDate') {
      return ['/admin-panel/knowledge/dates', entry.id];
    }
    return ['/admin-panel/knowledge/people', entry.id];
  }

  additionalInfoItems(entry: CalendarEntry): readonly string[] {
    const items: string[] = [];
    if (entry.period === 'nextMonth') {
      items.push(this.i18n.translate('dashboard.dates.nextMonth'));
    }
    if (entry.annualDate.year !== null) {
      const years = entry.occurrenceYear - entry.annualDate.year;
      if (years >= 0) {
        const category = new Intl.PluralRules(this.i18n.dateLocale()).select(years);
        const suffix = pluralSuffix(category);
        const prefix = entry.kind === 'birthday' ? 'age' : 'anniversary';
        items.push(this.i18n.translate(`dashboard.dates.${prefix}.${suffix}`, { count: years }));
      }
    }
    return items;
  }

  private readCollapsedSectionKeys(
    username: string | undefined,
    knownKeys: ReadonlySet<string>,
  ): ReadonlySet<string> {
    if (username === undefined) return new Set<string>();
    const storage = this.browserStorage();
    if (storage === null) return new Set<string>();
    try {
      const stored = storage.getItem(dashboardSectionStorageKey(username));
      if (stored === null) return new Set<string>();
      const parsed: unknown = JSON.parse(stored);
      if (!Array.isArray(parsed)) return new Set<string>();
      return new Set(
        parsed.filter(
          (sectionKey): sectionKey is string =>
            typeof sectionKey === 'string' && knownKeys.has(sectionKey),
        ),
      );
    } catch {
      return new Set<string>();
    }
  }

  private writeCollapsedSectionKeys(username: string | undefined): void {
    if (username === undefined) return;
    const storage = this.browserStorage();
    if (storage === null) return;
    try {
      storage.setItem(
        dashboardSectionStorageKey(username),
        JSON.stringify([...this.collapsedSectionKeys()].sort()),
      );
    } catch {
      return;
    }
  }

  private browserStorage(): Storage | null {
    try {
      return this.document.defaultView?.localStorage ?? null;
    } catch {
      return null;
    }
  }
}

function dashboardSectionStorageKey(username: string): string {
  return `adminDashboardSections:v1:${username}`;
}

function browserLocalDate(value: Date): string {
  const year = String(value.getFullYear()).padStart(4, '0');
  const month = String(value.getMonth() + 1).padStart(2, '0');
  const day = String(value.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function pluralSuffix(category: Intl.LDMLPluralRule): 'one' | 'few' | 'many' | 'other' {
  if (category === 'one' || category === 'few' || category === 'many') return category;
  return 'other';
}
