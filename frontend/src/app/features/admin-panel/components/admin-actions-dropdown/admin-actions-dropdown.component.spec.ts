import { ComponentFixture, TestBed } from '@angular/core/testing';
import { AdminAction, AdminActionsDropdownComponent } from './admin-actions-dropdown.component';

describe('AdminActionsDropdownComponent', () => {
  let fixture: ComponentFixture<AdminActionsDropdownComponent>;
  const actions: readonly AdminAction[] = [
    { id: 'edit', label: 'Редактировать', destructive: false, disabled: false },
    { id: 'delete', label: 'Удалить', destructive: true, disabled: false },
  ];

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AdminActionsDropdownComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(AdminActionsDropdownComponent);
    fixture.componentRef.setInput('actions', actions);
    fixture.componentRef.setInput('buttonLabel', 'Действия');
    fixture.componentRef.setInput('ariaLabel', 'Действия');
    fixture.componentRef.setInput('destructiveActionLabel', 'опасное действие');
    fixture.componentRef.setInput('testId', 'article-actions-typed-articles');
    fixture.detectChanges();
  });

  it('opens and closes an accessible actions dropdown', () => {
    const toggle = dropdownToggle();
    const menu = dropdownMenu();

    expect(toggle.textContent).toContain('Действия');
    expect(toggle.getAttribute('aria-expanded')).toBe('false');
    expect(menu.classList).not.toContain('show');

    toggle.click();
    fixture.detectChanges();

    expect(toggle.getAttribute('aria-expanded')).toBe('true');
    expect(menu.classList).toContain('show');

    document.body.click();
    fixture.detectChanges();

    expect(toggle.getAttribute('aria-expanded')).toBe('false');
    expect(menu.classList).not.toContain('show');
  });

  it('opens the menu with stylesheet-owned positioning for strict style-src-attr CSP', () => {
    const toggle = dropdownToggle();

    toggle.click();
    fixture.detectChanges();
    const menu = dropdownMenu();

    expect(menu.getAttribute('data-bs-popper')).toBe('static');
    expect(menu.classList).toContain('dropdown-menu');
    expect(menu.getAttribute('style')).toBeNull();
  });

  it('emits the selected action and marks destructive actions', () => {
    const selected = jest.fn();
    fixture.componentInstance.actionSelected.subscribe(selected);

    dropdownToggle().click();
    fixture.detectChanges();
    const deleteAction = fixture.nativeElement.querySelector(
      '[data-testid="article-actions-typed-articles-delete"]',
    ) as HTMLButtonElement;
    deleteAction.click();
    fixture.detectChanges();

    expect(deleteAction.classList).toContain('text-danger');
    expect(deleteAction.getAttribute('aria-label')).toBe('Удалить, опасное действие');
    expect(selected).toHaveBeenCalledWith('delete');
    expect(dropdownMenu().classList).not.toContain('show');
  });

  it('hides unavailable actions instead of rendering disabled buttons', () => {
    fixture.componentRef.setInput('actions', [
      { id: 'edit', label: 'Редактировать', destructive: false, disabled: false },
      { id: 'delete', label: 'Удалить', destructive: true, disabled: true },
    ]);
    fixture.detectChanges();

    dropdownToggle().click();
    fixture.detectChanges();

    expect(
      fixture.nativeElement.querySelector('[data-testid="article-actions-typed-articles-edit"]'),
    ).not.toBeNull();
    expect(
      fixture.nativeElement.querySelector('[data-testid="article-actions-typed-articles-delete"]'),
    ).toBeNull();
  });

  it('hides the dropdown trigger when every action is unavailable', () => {
    fixture.componentRef.setInput('actions', [
      { id: 'delete', label: 'Удалить', destructive: true, disabled: true },
    ]);
    fixture.detectChanges();

    expect(
      fixture.nativeElement.querySelector('[data-testid="article-actions-typed-articles-toggle"]'),
    ).toBeNull();
    expect(
      fixture.nativeElement.querySelector('[data-testid="article-actions-typed-articles-menu"]'),
    ).toBeNull();
  });

  function dropdownToggle(): HTMLButtonElement {
    const toggle = fixture.nativeElement.querySelector(
      '[data-testid="article-actions-typed-articles-toggle"]',
    ) as HTMLButtonElement | null;
    expect(toggle).not.toBeNull();
    return toggle as HTMLButtonElement;
  }

  function dropdownMenu(): HTMLElement {
    const menu = fixture.nativeElement.querySelector(
      '[data-testid="article-actions-typed-articles-menu"]',
    ) as HTMLElement | null;
    expect(menu).not.toBeNull();
    return menu as HTMLElement;
  }
});
