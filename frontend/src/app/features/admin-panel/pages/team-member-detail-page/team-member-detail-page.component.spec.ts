import { ComponentFixture, TestBed } from '@angular/core/testing';
import { WritableSignal, signal } from '@angular/core';
import { ActivatedRoute, Router, provideRouter } from '@angular/router';
import { of } from 'rxjs';
import { AccountInfo, AuthService } from '../../../../core/auth/auth.service';
import { NotificationService } from '../../../../core/notifications/notification.service';
import { provideI18nTesting } from '../../../../testing/i18n-testing';
import { ManagedAccount } from '../../models/team-workspace.model';
import { TeamWorkspaceService } from '../../services/team-workspace.service';
import { TeamMemberDetailPageComponent } from './team-member-detail-page.component';

describe('TeamMemberDetailPageComponent', () => {
  let fixture: ComponentFixture<TeamMemberDetailPageComponent>;
  let service: {
    getAccount: jest.Mock;
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
      getAccount: jest.fn().mockReturnValue(of(account())),
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
      imports: [TeamMemberDetailPageComponent],
      providers: [
        provideRouter([]),
        provideI18nTesting(),
        {
          provide: ActivatedRoute,
          useValue: {
            snapshot: {
              paramMap: {
                get: (key: string) => (key === 'username' ? 'AdminUser' : null),
              },
            },
          },
        },
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
    fixture = TestBed.createComponent(TeamMemberDetailPageComponent);
    fixture.detectChanges();
  });

  it('loads and renders readonly team member detail', () => {
    expect(service.getAccount).toHaveBeenCalledWith('AdminUser');
    expect(fixture.nativeElement.textContent).toContain('AdminUser');
    expect(fixture.nativeElement.textContent).toContain('Администратор');
    expect(fixture.nativeElement.textContent).toContain('Активен');
    expect(queryByTestId('team-detail-actions-toggle')).toBeNull();
  });

  it('renders owner account role labels', () => {
    service.getAccount.mockReturnValue(of(account({ username: 'OwnerUser', role: 'owner' })));
    fixture.componentInstance.loadAccount();
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('OwnerUser');
    expect(fixture.nativeElement.textContent).toContain('Владелец');
  });

  it('updates role and password through modal forms', () => {
    currentUser.set({ username: 'owner', role: 'owner' });
    fixture.detectChanges();
    openActions();
    elementByTestId<HTMLButtonElement>('team-detail-actions-role').click();
    fixture.detectChanges();
    setInputValue('team-role-role', 'moderator');
    submitForm('team-role-form');

    openActions();
    elementByTestId<HTMLButtonElement>('team-detail-actions-password').click();
    fixture.detectChanges();
    setInputValue('team-password-password', 'new-password');
    submitForm('team-password-form');

    expect(service.updateAccountRole).toHaveBeenCalledWith('AdminUser', 'moderator');
    expect(service.updateAccountPassword).toHaveBeenCalledWith('AdminUser', 'new-password');
    expect(notifications.success).toHaveBeenCalledWith('Роль обновлена.');
    expect(notifications.success).toHaveBeenCalledWith('Пароль обновлён.');
  });

  it('deactivates and deletes the current detail account with confirmation', () => {
    currentUser.set({ username: 'owner', role: 'owner' });
    fixture.detectChanges();
    jest.spyOn(window, 'confirm').mockReturnValue(true);

    fixture.componentInstance.deactivateAccount();
    fixture.componentInstance.deleteAccount();

    expect(service.deactivateAccount).toHaveBeenCalledWith('AdminUser');
    expect(service.deleteAccount).toHaveBeenCalledWith('AdminUser');
    expect(notifications.success).toHaveBeenCalledWith('Участник деактивирован.');
    expect(notifications.success).toHaveBeenCalledWith('Участник удалён.');
    expect(router.navigateByUrl).toHaveBeenCalledWith('/admin-panel/workspace/team');
  });

  it('hides unavailable self actions but allows self password updates', () => {
    currentUser.set({ username: 'AdminUser', role: 'admin' });
    fixture.detectChanges();

    openActions();

    expect(queryByTestId('team-detail-actions-role')).toBeNull();
    expect(queryByTestId('team-detail-actions-deactivate')).toBeNull();
    expect(queryByTestId('team-detail-actions-delete')).toBeNull();
    expect(elementByTestId<HTMLButtonElement>('team-detail-actions-password').disabled).toBe(false);
  });

  it('hides owner and admin detail actions from admins', () => {
    service.getAccount.mockReturnValue(of(account({ username: 'OwnerUser', role: 'owner' })));
    fixture.componentInstance.loadAccount();
    fixture.detectChanges();

    expect(queryByTestId('team-detail-actions-toggle')).toBeNull();

    service.getAccount.mockReturnValue(of(account({ username: 'OtherAdmin', role: 'admin' })));
    fixture.componentInstance.loadAccount();
    fixture.detectChanges();

    expect(queryByTestId('team-detail-actions-toggle')).toBeNull();
  });

  it('lets owners manage admin details with admin and moderator role options', () => {
    currentUser.set({ username: 'owner', role: 'owner' });
    service.getAccount.mockReturnValue(of(account({ username: 'OtherAdmin', role: 'admin' })));
    fixture.componentInstance.loadAccount();
    fixture.detectChanges();

    openActions();
    expect(elementByTestId<HTMLButtonElement>('team-detail-actions-role').disabled).toBe(false);
    expect(elementByTestId<HTMLButtonElement>('team-detail-actions-password').disabled).toBe(false);
    expect(elementByTestId<HTMLButtonElement>('team-detail-actions-deactivate').disabled).toBe(
      false,
    );
    expect(elementByTestId<HTMLButtonElement>('team-detail-actions-delete').disabled).toBe(false);

    elementByTestId<HTMLButtonElement>('team-detail-actions-role').click();
    fixture.detectChanges();
    expect(selectOptionValues('team-role-role')).toEqual(['admin', 'moderator']);
  });

  function openActions(): void {
    elementByTestId<HTMLButtonElement>('team-detail-actions-toggle').click();
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

  function queryByTestId(testId: string): Element | null {
    return fixture.nativeElement.querySelector(`[data-testid="${testId}"]`) as Element | null;
  }
});

function account(overrides: Partial<ManagedAccount> = {}): ManagedAccount {
  return {
    username: 'AdminUser',
    role: 'admin',
    isActive: true,
    ...overrides,
  };
}
