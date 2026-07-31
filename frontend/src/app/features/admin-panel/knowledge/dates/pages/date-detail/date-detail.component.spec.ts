import { Component, input, output } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { ActivatedRoute, Router, convertToParamMap, provideRouter } from '@angular/router';
import { Subject, of } from 'rxjs';
import { MarkdownEditorComponent } from '../../../../../../core/editor/markdown-editor.component';
import { NotificationService } from '../../../../../../core/notifications/notification.service';
import { provideI18nTesting } from '../../../../../../testing/i18n-testing';
import { PersonDetail } from '../../../people/models/people.model';
import { PeopleService } from '../../../people/services/people.service';
import { KnowledgeDateDetail } from '../../models/dates.model';
import { KnowledgeDatesService } from '../../services/dates.service';
import { DateDetailComponent } from './date-detail.component';

const DATE: KnowledgeDateDetail = {
  id: 'date-1',
  displayName: 'Годовщина',
  date: { day: 29, month: 2, year: null },
  description: '<script>alert(1)</script>',
  relatedPeople: [{ id: 'person-1', displayName: 'Иван Иванов' }],
  tags: [{ id: 'tag-1', name: 'Семья', color: '#ffffff' }],
  attachments: [
    {
      id: 'file-1',
      itemId: 'date-1',
      kind: 'attachment',
      mimeType: 'application/pdf',
      sizeBytes: 1024,
      name: 'Документ',
      originalName: 'document.pdf',
      contentPath: '/api/admin/knowledge/files/file-1/content',
      createdAt: '2026-01-01T00:00:00+00:00',
      updatedAt: '2026-01-01T00:00:00+00:00',
    },
  ],
  createdAt: '2026-01-01T00:00:00+00:00',
  updatedAt: '2026-01-02T00:00:00+00:00',
};

const PERSON: PersonDetail = {
  id: 'person-2',
  displayName: 'Пётр Петров',
  lastName: 'Петров',
  firstName: 'Пётр',
  middleName: '',
  email: '',
  phone: '',
  telegram: '',
  birthday: null,
  description: '',
  tags: [],
  relationships: [],
  relatedDates: [],
  photo: null,
  attachments: [],
  createdAt: DATE.createdAt,
  updatedAt: DATE.updatedAt,
};

describe('DateDetailComponent', () => {
  let fixture: ComponentFixture<DateDetailComponent>;
  let datesService: Record<string, jest.Mock>;
  let peopleService: Record<string, jest.Mock>;
  let notifications: { success: jest.Mock; error: jest.Mock };
  let router: Router;

  beforeEach(async () => {
    datesService = {
      getDate: jest.fn().mockReturnValue(of(DATE)),
      updateDate: jest.fn().mockReturnValue(of(DATE)),
      deleteDate: jest.fn().mockReturnValue(of(void 0)),
      uploadAttachment: jest.fn().mockReturnValue(of(DATE.attachments[0])),
      renameAttachment: jest.fn().mockReturnValue(of(DATE.attachments[0])),
      deleteAttachment: jest.fn().mockReturnValue(of(void 0)),
      getFileContent: jest.fn().mockReturnValue(of(new Blob(['private']))),
    };
    peopleService = {
      listTags: jest.fn().mockReturnValue(of(DATE.tags)),
      listPeople: jest.fn().mockReturnValue(of({ totalCount: 1, totalPages: 1, people: [PERSON] })),
      createTag: jest.fn().mockReturnValue(
        of({
          id: 'tag-2',
          name: 'Друзья',
          createdAt: DATE.createdAt,
          updatedAt: DATE.updatedAt,
        }),
      ),
      updateTag: jest.fn(),
      deleteTag: jest.fn(),
    };
    notifications = { success: jest.fn(), error: jest.fn() };

    await TestBed.configureTestingModule({
      imports: [DateDetailComponent],
      providers: [
        provideRouter([]),
        provideI18nTesting(),
        {
          provide: ActivatedRoute,
          useValue: {
            snapshot: { paramMap: convertToParamMap({ id: 'date-1' }) },
          },
        },
        { provide: KnowledgeDatesService, useValue: datesService },
        { provide: PeopleService, useValue: peopleService },
        { provide: NotificationService, useValue: notifications },
      ],
    })
      .overrideComponent(DateDetailComponent, {
        remove: { imports: [MarkdownEditorComponent] },
        add: { imports: [MarkdownEditorStubComponent] },
      })
      .compileComponents();

    router = TestBed.inject(Router);
    fixture = TestBed.createComponent(DateDetailComponent);
    fixture.detectChanges();
  });

  afterEach(() => fixture.destroy());

  it('loads a yearless leap date and disables inline image uploads', () => {
    expect(fixture.componentInstance.dateForm.controls.date.getRawValue()).toEqual({
      day: '29',
      month: '2',
      year: '',
    });
    const editor = fixture.debugElement.query(By.directive(MarkdownEditorStubComponent))
      .componentInstance as MarkdownEditorStubComponent;
    expect(editor.imageUploadsEnabled()).toBe(false);
  });

  it('marks only required date fields with red asterisks', () => {
    const markers = Array.from(
      fixture.nativeElement.querySelectorAll('.required-marker'),
    ) as HTMLElement[];
    const yearLabel = fixture.nativeElement.querySelector(
      'label[for="date-year"]',
    ) as HTMLLabelElement;

    expect(markers).toHaveLength(3);
    expect(markers.every((marker) => marker.classList.contains('text-danger'))).toBe(true);
    expect(yearLabel.textContent?.trim()).toBe('Год начала');
    expect(yearLabel.querySelector('.required-marker')).toBeNull();
  });

  it('adds and removes People without duplicates and sends explicit relations and tags', () => {
    const component = fixture.componentInstance;
    component.addPerson(PERSON);
    component.addPerson(PERSON);
    component.toggleTag('tag-1');
    component.toggleTag('tag-2');
    component.removePerson('person-1');
    component.dateForm.controls.displayName.setValue(' Обновлённая дата ');
    component.setDescription('Описание');
    component.saveDate();

    expect(datesService.updateDate).toHaveBeenCalledWith('date-1', {
      displayName: 'Обновлённая дата',
      date: { day: 29, month: 2, year: null },
      description: 'Описание',
      tagIds: ['tag-2'],
      personIds: ['person-2'],
    });
    expect(notifications.success).toHaveBeenCalled();
  });

  it('adds People from search suggestions instead of rendering every candidate as a button', () => {
    expect(
      fixture.nativeElement.querySelector('[data-testid="date-person-suggestion-person-2"]'),
    ).toBeNull();

    const search = fixture.nativeElement.querySelector(
      '[data-testid="date-people-search"]',
    ) as HTMLInputElement;
    search.value = 'Пётр';
    search.dispatchEvent(new Event('input'));
    fixture.detectChanges();

    const suggestion = fixture.nativeElement.querySelector(
      '[data-testid="date-person-suggestion-person-2"]',
    ) as HTMLButtonElement;
    expect(search.getAttribute('role')).toBe('combobox');
    expect(suggestion).not.toBeNull();
    suggestion.click();
    fixture.detectChanges();

    expect(fixture.componentInstance.selectedPeople()).toContainEqual({
      id: 'person-2',
      displayName: 'Пётр Петров',
    });
    expect(
      fixture.nativeElement.querySelector('[data-testid="date-person-suggestion-person-2"]'),
    ).toBeNull();
  });

  it('collapses more than ten related People and reveals the complete list on demand', () => {
    datesService.getDate.mockReturnValue(
      of({
        ...DATE,
        relatedPeople: Array.from({ length: 11 }, (_, index) => ({
          id: `person-${index + 1}`,
          displayName: `Человек ${index + 1}`,
        })),
      }),
    );
    fixture.componentInstance.loadDate();
    fixture.detectChanges();

    expect(
      fixture.nativeElement.querySelectorAll('[data-testid^="date-related-person-"]'),
    ).toHaveLength(10);

    const toggle = fixture.nativeElement.querySelector(
      '[data-testid="date-related-people-toggle"]',
    ) as HTMLButtonElement;
    toggle.click();
    fixture.detectChanges();

    expect(toggle.getAttribute('aria-expanded')).toBe('true');
    expect(
      fixture.nativeElement.querySelectorAll('[data-testid^="date-related-person-"]'),
    ).toHaveLength(11);
  });

  it('creates a knowledge tag from Date tag management', () => {
    const manage = fixture.nativeElement.querySelector(
      '[data-testid="date-tags-manage"]',
    ) as HTMLButtonElement;
    expect(manage).not.toBeNull();
    manage.click();
    fixture.detectChanges();

    const input = fixture.nativeElement.querySelector(
      '[data-testid="date-tag-draft"]',
    ) as HTMLInputElement;
    input.value = ' Друзья ';
    input.dispatchEvent(new Event('input'));
    (
      fixture.nativeElement.querySelector('[data-testid="date-tag-save"]') as HTMLButtonElement
    ).click();

    expect(peopleService.createTag).toHaveBeenCalledWith('Друзья');
  });

  it('shows a one-kilobyte attachment in kilobytes instead of zero megabytes', () => {
    const size = fixture.nativeElement.querySelector(
      '[data-testid="date-attachment-size-file-1"]',
    ) as HTMLElement;

    expect(size.textContent?.toLocaleUpperCase('ru-RU')).toContain('КБ');
    expect(size.textContent?.toLocaleUpperCase('ru-RU')).not.toContain('МБ');
  });

  it('rejects an invalid future date before saving', () => {
    fixture.componentInstance.dateForm.controls.date.setValue({
      day: '1',
      month: '1',
      year: '9999',
    });
    fixture.componentInstance.saveDate();

    expect(datesService.updateDate).not.toHaveBeenCalled();
    expect(notifications.error).toHaveBeenCalled();
  });

  it('keeps the latest People search and ignores the stale response', () => {
    const older = new Subject<{
      totalCount: number;
      totalPages: number;
      people: PersonDetail[];
    }>();
    const latest = new Subject<{
      totalCount: number;
      totalPages: number;
      people: PersonDetail[];
    }>();
    peopleService.listPeople.mockReset().mockReturnValueOnce(older).mockReturnValueOnce(latest);

    fixture.componentInstance.searchPeople('old');
    fixture.componentInstance.searchPeople('new');
    latest.next({
      totalCount: 1,
      totalPages: 1,
      people: [{ ...PERSON, id: 'latest', displayName: 'Latest' }],
    });
    older.next({
      totalCount: 1,
      totalPages: 1,
      people: [{ ...PERSON, id: 'stale', displayName: 'Stale' }],
    });

    expect(fixture.componentInstance.personCandidates()).toContainEqual(
      expect.objectContaining({ id: 'latest' }),
    );
    expect(fixture.componentInstance.personCandidates()).not.toContainEqual(
      expect.objectContaining({ id: 'stale' }),
    );
  });

  it('downloads a private attachment and always revokes its object URL', () => {
    const createObjectURL = jest.fn().mockReturnValue('blob:attachment');
    const revokeObjectURL = jest.fn();
    Object.defineProperty(window.URL, 'createObjectURL', {
      configurable: true,
      value: createObjectURL,
    });
    Object.defineProperty(window.URL, 'revokeObjectURL', {
      configurable: true,
      value: revokeObjectURL,
    });
    jest.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation();

    fixture.componentInstance.downloadAttachment(DATE.attachments[0]!);

    expect(datesService.getFileContent).toHaveBeenCalledWith('file-1');
    expect(createObjectURL).toHaveBeenCalledTimes(1);
    expect(revokeObjectURL).toHaveBeenCalledWith('blob:attachment');
  });

  it('deletes and returns to the list while preserving query state', () => {
    const navigate = jest.spyOn(router, 'navigate').mockResolvedValue(true);
    jest.spyOn(window, 'confirm').mockReturnValue(true);

    fixture.componentInstance.deleteDate();

    expect(datesService.deleteDate).toHaveBeenCalledWith('date-1');
    expect(navigate).toHaveBeenCalledWith(['/admin-panel/knowledge/dates'], {
      queryParamsHandling: 'preserve',
    });
  });
});

@Component({
  selector: 'app-markdown-editor',
  standalone: true,
  template: '',
})
class MarkdownEditorStubComponent {
  readonly value = input.required<string>();
  readonly language = input.required<'ru' | 'en'>();
  readonly accessibleLabel = input.required<string>();
  readonly imageUploadsEnabled = input.required<boolean>();
  readonly valueChange = output<string>();
}
