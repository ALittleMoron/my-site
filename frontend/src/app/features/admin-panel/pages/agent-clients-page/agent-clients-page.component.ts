import { DOCUMENT } from '@angular/common';
import {
  ChangeDetectionStrategy,
  Component,
  DestroyRef,
  OnInit,
  computed,
  inject,
  signal,
} from '@angular/core';
import { takeUntilDestroyed, toSignal } from '@angular/core/rxjs-interop';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { startWith } from 'rxjs';
import { I18nService } from '../../../../core/i18n/i18n.service';
import { TranslatePipe } from '../../../../core/i18n/translate.pipe';
import { ModalScrollDirective } from '../../../../core/layout/modal-scroll.directive';
import { ApiError } from '../../../../core/models/api-error.model';
import { NotificationService } from '../../../../core/notifications/notification.service';
import { EmptyStateComponent } from '../../../../shared/ui/empty-state/empty-state.component';
import { ErrorMessageComponent } from '../../../../shared/ui/error-message/error-message.component';
import { LoadingSpinnerComponent } from '../../../../shared/ui/loading-spinner/loading-spinner.component';
import { formatLocalizedDate } from '../../../../shared/utils/localized-date';
import { AdminControlValidationStateDirective } from '../../directives/admin-control-validation-state.directive';
import {
  AgentAuditCursor,
  AgentAuditEvent,
  AgentAuditEventPage,
  AgentClient,
  AgentClientRegistrationResult,
  AgentScope,
} from '../../models/agent-client-workspace.model';
import { AdminUnsavedChangesSource } from '../../services/admin-unsaved-changes.service';
import { AdminUnsavedChangesService } from '../../services/admin-unsaved-changes.service';
import { AgentClientWorkspaceService } from '../../services/agent-client-workspace.service';

interface AgentRegistrationForm {
  name: FormControl<string>;
  csrPem: FormControl<string>;
}

interface ScopeOption {
  value: AgentScope;
  labelKey: string;
}

const SCOPE_OPTIONS: readonly ScopeOption[] = [
  { value: 'matrix.queue.claim', labelKey: 'adminAgentClients.scope.queueClaim' },
  { value: 'matrix.context.read', labelKey: 'adminAgentClients.scope.contextRead' },
  { value: 'matrix.resources.read', labelKey: 'adminAgentClients.scope.resourcesRead' },
  { value: 'matrix.draft.create', labelKey: 'adminAgentClients.scope.draftCreate' },
];

const AGENT_AUDIT_PAGE_SIZE = 50;

@Component({
  selector: 'app-agent-clients-page',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    TranslatePipe,
    AdminControlValidationStateDirective,
    LoadingSpinnerComponent,
    ErrorMessageComponent,
    EmptyStateComponent,
    ModalScrollDirective,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './agent-clients-page.component.html',
})
export class AgentClientsPageComponent implements OnInit {
  private readonly service = inject(AgentClientWorkspaceService);
  private readonly notifications = inject(NotificationService);
  private readonly i18n = inject(I18nService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly document = inject(DOCUMENT);
  private readonly unsavedChanges = inject(AdminUnsavedChangesService);

  readonly clients = signal<AgentClient[]>([]);
  readonly loading = signal(false);
  readonly loadError = signal<ApiError | null>(null);
  readonly registrationOpen = signal(false);
  readonly registering = signal(false);
  readonly registrationErrorKey = signal<string | null>(null);
  readonly selectedScopes = signal<ReadonlySet<AgentScope>>(new Set<AgentScope>());
  readonly issuedCredentials = signal<AgentClientRegistrationResult | null>(null);
  readonly revokingClientId = signal<string | null>(null);
  readonly auditClient = signal<AgentClient | null>(null);
  readonly auditEvents = signal<AgentAuditEvent[]>([]);
  readonly auditLoading = signal(false);
  readonly auditError = signal(false);
  readonly auditCursor = signal<AgentAuditCursor | null>(null);
  readonly auditLoadingMore = signal(false);
  readonly auditLoadMoreError = signal(false);
  readonly auditReachedEnd = signal(false);
  readonly scopeOptions = SCOPE_OPTIONS;
  readonly hasClients = computed(() => this.clients().length > 0);
  readonly registrationForm = new FormGroup<AgentRegistrationForm>({
    name: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    csrPem: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
  });
  private readonly registrationFormValue = toSignal(
    this.registrationForm.valueChanges.pipe(startWith(this.registrationForm.getRawValue())),
    { requireSync: true },
  );
  private readonly registrationDraft = computed(() => ({
    form: this.registrationFormValue(),
    scopes: [...this.selectedScopes()].sort(),
  }));
  private readonly registrationUnsavedSource: AdminUnsavedChangesSource;
  private auditRequestGeneration = 0;

  constructor() {
    const scope = this.unsavedChanges.createScope(this.destroyRef);
    this.registrationUnsavedSource = scope.registerSource(
      this.registrationDraft,
      this.registrationOpen,
    );
  }

  ngOnInit(): void {
    this.loadClients();
  }

  loadClients(): void {
    this.loading.set(true);
    this.loadError.set(null);
    this.service
      .listClients()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (clients) => {
          this.clients.set(clients);
          this.loading.set(false);
        },
        error: (error: ApiError) => {
          this.loadError.set(error);
          this.loading.set(false);
          this.notifications.error(this.i18n.translate('adminAgentClients.loadError'));
        },
      });
  }

  openRegistration(): void {
    this.registrationForm.reset({ name: '', csrPem: '' });
    this.selectedScopes.set(new Set<AgentScope>());
    this.registrationErrorKey.set(null);
    this.registrationUnsavedSource.commit();
    this.registrationOpen.set(true);
  }

  closeRegistration(): void {
    if (this.registering() || !this.unsavedChanges.confirmDiscard()) return;
    this.registrationOpen.set(false);
    this.registrationErrorKey.set(null);
    this.registrationUnsavedSource.commit();
  }

  toggleScope(scope: AgentScope, selected: boolean): void {
    this.selectedScopes.update((current) => {
      const next = new Set(current);
      if (selected) next.add(scope);
      else next.delete(scope);
      return next;
    });
  }

  onScopeChange(scope: AgentScope, event: Event): void {
    const target = event.target as HTMLInputElement | null;
    if (target !== null) this.toggleScope(scope, target.checked);
  }

  registerClient(): void {
    this.registrationForm.markAllAsTouched();
    if (this.registrationForm.invalid || this.selectedScopes().size === 0) {
      this.notifications.error(this.i18n.translate('adminAgentClients.validationError'));
      return;
    }
    const value = this.registrationForm.getRawValue();
    this.registering.set(true);
    this.registrationErrorKey.set(null);
    this.service
      .registerClient({
        name: value.name.trim(),
        scopes: [...this.selectedScopes()],
        csrPem: value.csrPem.trim(),
      })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (result) => {
          this.registering.set(false);
          this.registrationOpen.set(false);
          this.clients.update((clients) => [result.client, ...clients]);
          this.issuedCredentials.set(result);
          this.registrationForm.reset({ name: '', csrPem: '' });
          this.selectedScopes.set(new Set<AgentScope>());
          this.registrationUnsavedSource.commit();
          this.notifications.success(this.i18n.translate('adminAgentClients.registered'));
        },
        error: (error: ApiError) => {
          this.registering.set(false);
          const errorKey =
            error.status === 409
              ? 'adminAgentClients.duplicateName'
              : 'adminAgentClients.registerError';
          this.registrationErrorKey.set(errorKey);
          this.notifications.error(this.i18n.translate(errorKey));
        },
      });
  }

  dismissIssuedCredentials(): void {
    this.issuedCredentials.set(null);
  }

  revokeClient(client: AgentClient): void {
    if (client.status === 'revoked' || this.revokingClientId() !== null) return;
    const confirmed =
      this.document.defaultView?.confirm(
        this.i18n.translate('adminAgentClients.confirmRevoke', { name: client.name }),
      ) ?? false;
    if (!confirmed) return;
    this.revokingClientId.set(client.id);
    this.service
      .revokeClient(client.id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.revokingClientId.set(null);
          this.clients.update((clients) =>
            clients.map((item) =>
              item.id === client.id ? { ...item, status: 'revoked' as const } : item,
            ),
          );
          this.notifications.success(this.i18n.translate('adminAgentClients.revoked'));
        },
        error: () => {
          this.revokingClientId.set(null);
          this.notifications.error(this.i18n.translate('adminAgentClients.revokeError'));
        },
      });
  }

  loadAudit(client: AgentClient): void {
    const requestGeneration = ++this.auditRequestGeneration;
    this.auditClient.set(client);
    this.auditEvents.set([]);
    this.auditCursor.set(null);
    this.auditError.set(false);
    this.auditLoadMoreError.set(false);
    this.auditLoadingMore.set(false);
    this.auditReachedEnd.set(false);
    this.auditLoading.set(true);
    this.requestAuditPage(client, null, true, requestGeneration);
  }

  retryAudit(): void {
    const client = this.auditClient();
    if (client !== null && !this.auditLoading()) this.loadAudit(client);
  }

  loadMoreAudit(): void {
    const client = this.auditClient();
    const cursor = this.auditCursor();
    if (
      client === null ||
      cursor === null ||
      this.auditLoading() ||
      this.auditLoadingMore() ||
      this.auditReachedEnd()
    ) {
      return;
    }
    this.auditLoadingMore.set(true);
    this.auditLoadMoreError.set(false);
    this.requestAuditPage(client, cursor, false, this.auditRequestGeneration);
  }

  private requestAuditPage(
    client: AgentClient,
    cursor: AgentAuditCursor | null,
    initial: boolean,
    requestGeneration: number,
  ): void {
    this.service
      .listAuditEvents(client.id, AGENT_AUDIT_PAGE_SIZE, cursor)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (page) => {
          if (!this.isCurrentAuditRequest(client.id, requestGeneration)) return;
          this.applyAuditPage(page, initial);
        },
        error: () => {
          if (!this.isCurrentAuditRequest(client.id, requestGeneration)) return;
          if (initial) {
            this.auditError.set(true);
            this.auditLoading.set(false);
            this.notifications.error(this.i18n.translate('adminAgentClients.auditLoadError'));
          } else {
            this.auditLoadMoreError.set(true);
            this.auditLoadingMore.set(false);
            this.notifications.error(this.i18n.translate('adminAgentClients.auditLoadMoreError'));
          }
        },
      });
  }

  private applyAuditPage(page: AgentAuditEventPage, initial: boolean): void {
    if (initial) {
      this.auditEvents.set(page.events);
      this.auditLoading.set(false);
    } else {
      const existingIds = new Set(this.auditEvents().map((event) => event.id));
      this.auditEvents.update((events) => [
        ...events,
        ...page.events.filter((event) => !existingIds.has(event.id)),
      ]);
      this.auditLoadingMore.set(false);
    }
    this.auditCursor.set(page.nextCursor);
    this.auditReachedEnd.set(page.nextCursor === null);
    this.auditError.set(false);
    this.auditLoadMoreError.set(false);
  }

  private isCurrentAuditRequest(clientId: string, requestGeneration: number): boolean {
    return requestGeneration === this.auditRequestGeneration && this.auditClient()?.id === clientId;
  }

  closeAudit(): void {
    this.auditRequestGeneration += 1;
    this.auditClient.set(null);
    this.auditEvents.set([]);
    this.auditCursor.set(null);
    this.auditError.set(false);
    this.auditLoading.set(false);
    this.auditLoadingMore.set(false);
    this.auditLoadMoreError.set(false);
    this.auditReachedEnd.set(false);
  }

  formatDate(value: string): string {
    return formatLocalizedDate(value, this.i18n.dateLocale(), 'dateTime');
  }

  statusLabelKey(client: AgentClient): string {
    return `adminAgentClients.status.${client.status}`;
  }
}
