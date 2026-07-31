import { Component, input, output } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { ActivatedRoute, convertToParamMap, Router, provideRouter } from '@angular/router';
import { of, Subject } from 'rxjs';
import { MarkdownEditorComponent } from '../../../../../../core/editor/markdown-editor.component';
import { NotificationService } from '../../../../../../core/notifications/notification.service';
import { provideI18nTesting } from '../../../../../../testing/i18n-testing';
import { PersonDetail } from '../../models/people.model';
import { PeopleService } from '../../services/people.service';
import { PersonDetailComponent } from './person-detail.component';

const PERSON: PersonDetail = {
  id: 'person-1',
  displayName: 'Иванов Иван',
  lastName: 'Иванов',
  firstName: 'Иван',
  middleName: '',
  email: '',
  phone: '',
  telegram: '@ivanov',
  birthday: { day: 29, month: 2, year: null },
  description: '<script>alert(1)</script>',
  tags: [],
  relationships: [],
  relatedDates: [
    {
      id: 'date-1',
      displayName: 'Годовщина',
      date: { day: 29, month: 2, year: null },
    },
  ],
  photo: null,
  attachments: [],
  createdAt: '2026-01-01T00:00:00+00:00',
  updatedAt: '2026-01-01T00:00:00+00:00',
};

describe('PersonDetailComponent', () => {
  let fixture: ComponentFixture<PersonDetailComponent>;
  let peopleService: Record<string, jest.Mock>;
  let notifications: { success: jest.Mock; error: jest.Mock };
  let router: Router;

  beforeEach(async () => {
    peopleService = {
      getPerson: jest.fn().mockReturnValue(of(PERSON)),
      listTags: jest.fn().mockReturnValue(of([])),
      listRelationshipTypes: jest.fn().mockReturnValue(of([])),
      listPeople: jest.fn().mockReturnValue(of({ totalCount: 0, totalPages: 1, people: [] })),
      updatePerson: jest.fn().mockReturnValue(of(PERSON)),
      deletePerson: jest.fn().mockReturnValue(of(void 0)),
      getFileContent: jest.fn(),
      replacePhoto: jest.fn(),
      deletePhoto: jest.fn(),
      uploadAttachment: jest.fn(),
      renameAttachment: jest.fn(),
      deleteAttachment: jest.fn(),
      createTag: jest.fn(),
      updateTag: jest.fn(),
      deleteTag: jest.fn(),
      createRelationshipType: jest.fn(),
      updateRelationshipType: jest.fn(),
      deleteRelationshipType: jest.fn(),
    };
    notifications = { success: jest.fn(), error: jest.fn() };

    await TestBed.configureTestingModule({
      imports: [PersonDetailComponent],
      providers: [
        provideRouter([]),
        provideI18nTesting(),
        {
          provide: ActivatedRoute,
          useValue: {
            snapshot: { paramMap: convertToParamMap({ id: 'person-1' }) },
          },
        },
        { provide: PeopleService, useValue: peopleService },
        { provide: NotificationService, useValue: notifications },
      ],
    })
      .overrideComponent(PersonDetailComponent, {
        remove: { imports: [MarkdownEditorComponent] },
        add: { imports: [MarkdownEditorStubComponent] },
      })
      .compileComponents();

    router = TestBed.inject(Router);
    fixture = TestBed.createComponent(PersonDetailComponent);
    fixture.detectChanges();
  });

  afterEach(() => fixture.destroy());

  it('loads a yearless leap-day birthday and disables People image uploads', () => {
    expect(fixture.componentInstance.personForm.controls.birthday.getRawValue()).toEqual({
      day: '29',
      month: '2',
      year: '',
    });
    const editor = fixture.debugElement.query(By.directive(MarkdownEditorStubComponent))
      .componentInstance as MarkdownEditorStubComponent;
    expect(editor.imageUploadsEnabled()).toBe(false);
  });

  it('renders read-only memorable-date backlinks with localized dates', () => {
    const link = fixture.nativeElement.querySelector(
      'a[href="/admin-panel/knowledge/dates/date-1"]',
    ) as HTMLAnchorElement | null;

    expect(link?.textContent).toContain('Годовщина');
    expect(fixture.nativeElement.textContent).toContain('29');
  });

  it('loads and saves Telegram from the sticky form action footer', () => {
    const component = fixture.componentInstance;
    const telegramInput = fixture.nativeElement.querySelector(
      '#person-telegram',
    ) as HTMLInputElement | null;
    const footer = fixture.nativeElement.querySelector(
      '[data-testid="person-detail-action-footer"]',
    ) as HTMLElement | null;
    const save = fixture.nativeElement.querySelector(
      '[data-testid="person-detail-save"]',
    ) as HTMLButtonElement | null;

    expect(component.personForm.controls.telegram.value).toBe('@ivanov');
    expect(telegramInput?.value).toBe('@ivanov');
    expect(footer).not.toBeNull();
    expect(save).not.toBeNull();
    expect(footer?.contains(save)).toBe(true);

    if (telegramInput !== null) {
      telegramInput.value = ' @new_ivanov ';
      telegramInput.dispatchEvent(new Event('input'));
    }
    save?.click();

    expect(peopleService.updatePerson).toHaveBeenCalledWith(
      'person-1',
      expect.objectContaining({ telegram: '@new_ivanov' }),
    );

    component.personForm.controls.telegram.setValue('x'.repeat(256));
    save?.click();
    expect(peopleService.updatePerson).toHaveBeenCalledTimes(1);
    expect(notifications.error).toHaveBeenCalled();
  });

  it('deletes through the detail actions dropdown without a top save action', () => {
    const navigate = jest.spyOn(router, 'navigate').mockResolvedValue(true);
    jest.spyOn(window, 'confirm').mockReturnValue(true);

    const deleteAction = fixture.nativeElement.querySelector(
      '[data-testid="people-detail-actions-delete"]',
    ) as HTMLButtonElement | null;
    expect(deleteAction).not.toBeNull();
    expect(
      fixture.nativeElement.querySelectorAll('[data-testid="person-detail-save"]'),
    ).toHaveLength(1);
    deleteAction?.click();

    expect(peopleService.deletePerson).toHaveBeenCalledWith('person-1');
    expect(navigate).toHaveBeenCalledWith(['/admin-panel/knowledge/people'], {
      queryParamsHandling: 'preserve',
    });
  });

  it('blocks an invalid future birthday and sends explicit relationship batches', () => {
    const component = fixture.componentInstance;
    component.personForm.controls.birthday.setValue({
      day: '1',
      month: '1',
      year: '9999',
    });
    component.savePerson();
    expect(peopleService.updatePerson).not.toHaveBeenCalled();
    expect(notifications.error).toHaveBeenCalled();

    component.personForm.controls.birthday.setValue({
      day: '29',
      month: '2',
      year: '',
    });
    component.addRelationship();
    const relationship = component.relationshipForms.at(0);
    relationship.setValue({
      persistedId: '',
      relatedPersonId: 'person-2',
      relationshipTypeId: 'type-1',
      direction: 'forward',
      note: 'Работали вместе',
    });
    component.savePerson();

    expect(peopleService.updatePerson).toHaveBeenCalledWith(
      'person-1',
      expect.objectContaining({
        birthday: { day: 29, month: 2, year: null },
        relationshipChanges: {
          create: [
            {
              relatedPersonId: 'person-2',
              relationshipTypeId: 'type-1',
              direction: 'forward',
              note: 'Работали вместе',
            },
          ],
          update: [],
          deleteIds: [],
        },
      }),
    );
  });

  it('preserves list query state when navigating back', () => {
    const navigate = jest.spyOn(router, 'navigate').mockResolvedValue(true);
    fixture.componentInstance.back();
    expect(navigate).toHaveBeenCalledWith(['/admin-panel/knowledge/people'], {
      queryParamsHandling: 'preserve',
    });
  });

  it('keeps the latest relationship candidates and ignores an older error', () => {
    const olderResponse = new Subject<{
      totalCount: number;
      totalPages: number;
      people: PersonDetail[];
    }>();
    const latestResponse = new Subject<{
      totalCount: number;
      totalPages: number;
      people: PersonDetail[];
    }>();
    peopleService['listPeople']
      .mockReset()
      .mockReturnValueOnce(olderResponse)
      .mockReturnValueOnce(latestResponse);

    fixture.componentInstance.searchPeople('older');
    fixture.componentInstance.searchPeople('latest');
    latestResponse.next({
      totalCount: 1,
      totalPages: 1,
      people: [{ ...PERSON, id: 'latest-person', displayName: 'Latest Person' }],
    });
    olderResponse.next({
      totalCount: 1,
      totalPages: 1,
      people: [{ ...PERSON, id: 'older-person', displayName: 'Older Person' }],
    });
    olderResponse.error(new Error('stale request'));

    expect(fixture.componentInstance.personCandidateOptions()).toContainEqual({
      value: 'latest-person',
      label: 'Latest Person',
    });
    expect(fixture.componentInstance.personCandidateOptions()).not.toContainEqual({
      value: 'older-person',
      label: 'Older Person',
    });
    expect(notifications.error).not.toHaveBeenCalled();
  });

  it('ignores a stale photo response and revokes the current URL on destroy', () => {
    const firstPhoto = new Subject<Blob>();
    const secondPhoto = new Subject<Blob>();
    peopleService['getPerson'].mockReturnValue(
      of({
        ...PERSON,
        photo: {
          id: 'photo-1',
          itemId: 'person-1',
          kind: 'personPhoto',
          mimeType: 'image/webp',
          sizeBytes: 10,
          name: 'photo.webp',
          originalName: 'photo.webp',
          contentPath: '/api/admin/knowledge/files/photo-1/content',
          createdAt: PERSON.createdAt,
          updatedAt: PERSON.updatedAt,
        },
      }),
    );
    peopleService['getFileContent']
      .mockReturnValueOnce(firstPhoto)
      .mockReturnValueOnce(secondPhoto);
    const createObjectURL = jest.fn().mockReturnValue('blob:current-photo');
    const revokeObjectURL = jest.fn();
    Object.defineProperty(window.URL, 'createObjectURL', {
      configurable: true,
      value: createObjectURL,
    });
    Object.defineProperty(window.URL, 'revokeObjectURL', {
      configurable: true,
      value: revokeObjectURL,
    });

    fixture.componentInstance.loadPerson();
    fixture.componentInstance.loadPerson();
    firstPhoto.next(new Blob(['stale']));
    expect(createObjectURL).not.toHaveBeenCalled();

    secondPhoto.next(new Blob(['current']));
    expect(createObjectURL).toHaveBeenCalledTimes(1);
    fixture.destroy();
    expect(revokeObjectURL).toHaveBeenCalledWith('blob:current-photo');
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
