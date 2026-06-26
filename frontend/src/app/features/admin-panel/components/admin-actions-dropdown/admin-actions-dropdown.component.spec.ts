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

  it('positions the open menu under the trigger as a viewport overlay', () => {
    Object.defineProperty(window, 'innerWidth', { configurable: true, value: 1024 });
    const toggle = dropdownToggle();
    jest.spyOn(toggle, 'getBoundingClientRect').mockReturnValue({
      bottom: 132,
      height: 32,
      left: 512,
      right: 648,
      top: 100,
      width: 136,
      x: 512,
      y: 100,
      toJSON: () => ({}),
    });

    toggle.click();
    fixture.detectChanges();
    const menu = dropdownMenu();

    expect(menu.getAttribute('data-bs-popper')).toBe('static');
    expect(menu.style.position).toBe('fixed');
    expect(menu.style.top).toBe('132px');
    expect(menu.style.right).toBe('376px');
    expect(menu.style.zIndex).toBe('1055');
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
