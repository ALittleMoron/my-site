import { ComponentFixture, TestBed } from '@angular/core/testing';
import { WritableSignal, signal } from '@angular/core';
import { Router, provideRouter } from '@angular/router';
import { of, throwError } from 'rxjs';
import { AccountInfo, AuthService } from '../../../../core/auth/auth.service';
import { ApiError } from '../../../../core/models/api-error.model';
import { NotificationService } from '../../../../core/notifications/notification.service';
import { provideI18nTesting } from '../../../../testing/i18n-testing';
import { ManagedAccount, ManagedAccounts } from '../../models/team-workspace.model';
import { TeamWorkspaceService } from '../../services/team-workspace.service';
import { TeamPageComponent } from './team-page.component';

describe('TeamPageComponent', () => {
  let fixture: ComponentFixture<TeamPageComponent>;
  let service: {
    listAccounts: jest.Mock;
    createAccount: jest.Mock;
    updateAccountRole: jest.Mock;
    updateAccountPassword: jest.Mock;
    activateAccount: jest.Mock;
    deactivateAccount: jest.Mock;
    deleteAccount: jest.Mock;
  };
  let currentUser: WritableSignal<AccountInfo | null>;
  let router: Router;
  let notifications: {
    success: jest.Mock;
    error: jest.Mock;
  };

  beforeEach(async () => {
    service = {
      listAccounts: jest.fn().mockReturnValue(of(accountsList([account()]))),
      createAccount: jest.fn().mockReturnValue(of(account({ username: 'NewAdmin' }))),
      updateAccountRole: jest.fn().mockReturnValue(of(account({ role: 'moderator' }))),
      updateAccountPassword: jest.fn().mockReturnValue(of(account())),
      activateAccount: jest.fn().mockReturnValue(of(account())),
      deactivateAccount: jest.fn().mockReturnValue(of(account({ isActive: false }))),
      deleteAccount: jest.fn().mockReturnValue(of(undefined)),
    };
    currentUser = signal({ username: 'admin', role: 'admin' });
    notifications = {
      success: jest.fn(),
      error: jest.fn(),
    };

    await TestBed.configureTestingModule({
      imports: [TeamPageComponent],
      providers: [
        provideRouter([]),
        provideI18nTesting(),
        { provide: TeamWorkspaceService, useValue: service },
        { provide: NotificationService, useValue: notifications },
        {
          provide: AuthService,
          useValue: {
            currentUser,
          },
        },
      ],
    }).compileComponents();

    router = TestBed.inject(Router);
    jest.spyOn(router, 'navigateByUrl').mockResolvedValue(true);
    fixture = TestBed.createComponent(TeamPageComponent);
    fixture.detectChanges();
  });

  it('loads and renders the managed team list', () => {
    expect(service.listAccounts).toHaveBeenCalledWith({ page: 1, pageSize: 20 });
    expect(fixture.nativeElement.textContent).toContain('Команда');
    expect(fixture.nativeElement.textContent).toContain('AdminUser');
    expect(fixture.nativeElement.textContent).toContain('Администратор');
    expect(fixture.nativeElement.textContent).toContain('Активен');
  });

  it('renders owner accounts and owner role labels', () => {
    service.listAccounts.mockReturnValue(
      of(accountsList([account({ username: 'OwnerUser', role: 'owner' })])),
    );
    fixture.componentInstance.loadAccounts();
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('OwnerUser');
    expect(fixture.nativeElement.textContent).toContain('Владелец');
  });

  it('shows admin and moderator creation role options for owners', () => {
    currentUser.set({ username: 'owner', role: 'owner' });
    fixture.detectChanges();

    openCreateDialog();

    expect(selectOptionValues('team-create-role')).toEqual(['', 'admin', 'moderator']);
  });

  it('shows only moderator creation role options for admins', () => {
    openCreateDialog();

    expect(selectOptionValues('team-create-role')).toEqual(['', 'moderator']);
  });

  it('creates an active managed account and navigates to detail', () => {
    currentUser.set({ username: 'owner', role: 'owner' });
    fixture.detectChanges();
    openCreateDialog();

    setInputValue('team-create-username', 'NewAdmin');
    setInputValue('team-create-role', 'moderator');
    setInputValue('team-create-password', 'password123');
    submitForm('team-create-form');

    expect(service.createAccount).toHaveBeenCalledWith({
      username: 'NewAdmin',
      role: 'moderator',
      password: 'password123',
      isActive: true,
    });
    expect(notifications.success).toHaveBeenCalledWith('Участник создан.');
    expect(router.navigateByUrl).toHaveBeenCalledWith('/admin-panel/workspace/team/NewAdmin');
  });

  it('marks invalid usernames before calling the create endpoint', () => {
    openCreateDialog();

    setInputValue('team-create-username', 'кириллица');
    setInputValue('team-create-role', 'admin');
    setInputValue('team-create-password', 'password123');
    submitForm('team-create-form');

    const username = elementByTestId<HTMLInputElement>('team-create-username');
    expect(username.classList).toContain('is-invalid');
    expect(service.createAccount).not.toHaveBeenCalled();
    expect(notifications.error).toHaveBeenCalledWith('Проверьте поля участника.');
  });

  it('disables self role, deactivate, and delete actions in the row dropdown', () => {
    service.listAccounts.mockReturnValue(of(accountsList([account({ username: 'admin' })])));
    fixture.componentInstance.loadAccounts();
    fixture.detectChanges();

    openActions('admin');

    expect(elementByTestId<HTMLButtonElement>('team-actions-admin-role').disabled).toBe(true);
    expect(elementByTestId<HTMLButtonElement>('team-actions-admin-deactivate').disabled).toBe(true);
    expect(elementByTestId<HTMLButtonElement>('team-actions-admin-delete').disabled).toBe(true);
    expect(elementByTestId<HTMLButtonElement>('team-actions-admin-password').disabled).toBe(false);
  });

  it('makes owner and admin rows read-only for admins', () => {
    service.listAccounts.mockReturnValue(
      of(
        accountsList([
          account({ username: 'OwnerUser', role: 'owner' }),
          account({ username: 'OtherAdmin', role: 'admin' }),
        ]),
      ),
    );
    fixture.componentInstance.loadAccounts();
    fixture.detectChanges();

    openActions('OwnerUser');
    expect(elementByTestId<HTMLButtonElement>('team-actions-OwnerUser-role').disabled).toBe(true);
    expect(elementByTestId<HTMLButtonElement>('team-actions-OwnerUser-password').disabled).toBe(
      true,
    );
    expect(elementByTestId<HTMLButtonElement>('team-actions-OwnerUser-deactivate').disabled).toBe(
      true,
    );
    expect(elementByTestId<HTMLButtonElement>('team-actions-OwnerUser-delete').disabled).toBe(true);

    openActions('OtherAdmin');
    expect(elementByTestId<HTMLButtonElement>('team-actions-OtherAdmin-role').disabled).toBe(true);
    expect(elementByTestId<HTMLButtonElement>('team-actions-OtherAdmin-password').disabled).toBe(
      true,
    );
    expect(elementByTestId<HTMLButtonElement>('team-actions-OtherAdmin-deactivate').disabled).toBe(
      true,
    );
    expect(elementByTestId<HTMLButtonElement>('team-actions-OtherAdmin-delete').disabled).toBe(
      true,
    );
  });

  it('lets admins manage moderator rows except role changes', () => {
    service.listAccounts.mockReturnValue(
      of(accountsList([account({ username: 'Moderator1', role: 'moderator' })])),
    );
    fixture.componentInstance.loadAccounts();
    fixture.detectChanges();

    openActions('Moderator1');

    expect(elementByTestId<HTMLButtonElement>('team-actions-Moderator1-role').disabled).toBe(true);
    expect(elementByTestId<HTMLButtonElement>('team-actions-Moderator1-password').disabled).toBe(
      false,
    );
    expect(elementByTestId<HTMLButtonElement>('team-actions-Moderator1-deactivate').disabled).toBe(
      false,
    );
    expect(elementByTestId<HTMLButtonElement>('team-actions-Moderator1-delete').disabled).toBe(
      false,
    );
  });

  it('lets owners manage admin rows', () => {
    currentUser.set({ username: 'owner', role: 'owner' });
    service.listAccounts.mockReturnValue(
      of(accountsList([account({ username: 'OtherAdmin', role: 'admin' })])),
    );
    fixture.componentInstance.loadAccounts();
    fixture.detectChanges();

    openActions('OtherAdmin');

    expect(elementByTestId<HTMLButtonElement>('team-actions-OtherAdmin-role').disabled).toBe(false);
    expect(elementByTestId<HTMLButtonElement>('team-actions-OtherAdmin-password').disabled).toBe(
      false,
    );
    expect(elementByTestId<HTMLButtonElement>('team-actions-OtherAdmin-deactivate').disabled).toBe(
      false,
    );
    expect(elementByTestId<HTMLButtonElement>('team-actions-OtherAdmin-delete').disabled).toBe(
      false,
    );
  });

  it('activates, deactivates, and deletes accounts from row actions with feedback', () => {
    jest.spyOn(window, 'confirm').mockReturnValue(true);
    service.listAccounts.mockReturnValue(
      of(accountsList([account({ username: 'Moderator1', role: 'moderator', isActive: false })])),
    );
    fixture.componentInstance.loadAccounts();
    fixture.detectChanges();

    openActions('Moderator1');
    elementByTestId<HTMLButtonElement>('team-actions-Moderator1-activate').click();
    fixture.detectChanges();

    fixture.componentInstance.deactivateAccount(
      account({ username: 'Moderator1', role: 'moderator', isActive: true }),
    );
    fixture.componentInstance.deleteAccount(account({ username: 'Moderator1', role: 'moderator' }));

    expect(service.activateAccount).toHaveBeenCalledWith('Moderator1');
    expect(service.deactivateAccount).toHaveBeenCalledWith('Moderator1');
    expect(service.deleteAccount).toHaveBeenCalledWith('Moderator1');
    expect(notifications.success).toHaveBeenCalledWith('Участник активирован.');
    expect(notifications.success).toHaveBeenCalledWith('Участник деактивирован.');
    expect(notifications.success).toHaveBeenCalledWith('Участник удалён.');
  });

  it('shows an API error notification on create failure', () => {
    service.createAccount.mockReturnValue(throwError(() => apiError()));
    openCreateDialog();

    setInputValue('team-create-username', 'NewAdmin');
    setInputValue('team-create-role', 'moderator');
    setInputValue('team-create-password', 'password123');
    submitForm('team-create-form');

    expect(notifications.error).toHaveBeenCalledWith('Не удалось создать участника.');
  });

  function openCreateDialog(): void {
    elementByTestId<HTMLButtonElement>('team-create-open').click();
    fixture.detectChanges();
  }

  function openActions(username: string): void {
    elementByTestId<HTMLButtonElement>(`team-actions-${username}-toggle`).click();
    fixture.detectChanges();
  }

  function setInputValue(testId: string, value: string): void {
    const input = elementByTestId<HTMLInputElement | HTMLSelectElement>(testId);
    input.value = value;
    input.dispatchEvent(new Event('input'));
    input.dispatchEvent(new Event('change'));
    fixture.detectChanges();
  }

  function selectOptionValues(testId: string): string[] {
    const select = elementByTestId<HTMLSelectElement>(testId);
    return Array.from(select.options).map((option) => option.value);
  }

  function submitForm(testId: string): void {
    elementByTestId<HTMLFormElement>(testId).dispatchEvent(new Event('submit'));
    fixture.detectChanges();
  }

  function elementByTestId<T extends Element>(testId: string): T {
    const element = fixture.nativeElement.querySelector(`[data-testid="${testId}"]`) as T | null;
    expect(element).not.toBeNull();
    return element as T;
  }
});

function accountsList(accounts: ManagedAccount[]): ManagedAccounts {
  return {
    totalCount: accounts.length,
    totalPages: accounts.length > 0 ? 1 : 0,
    accounts,
  };
}

function account(overrides: Partial<ManagedAccount> = {}): ManagedAccount {
  return {
    username: 'AdminUser',
    role: 'admin',
    isActive: true,
    ...overrides,
  };
}

function apiError(): ApiError {
  return {
    code: 'bad_request',
    type: 'BadRequest',
    message: 'Bad request',
    location: null,
    attr: null,
  };
}
