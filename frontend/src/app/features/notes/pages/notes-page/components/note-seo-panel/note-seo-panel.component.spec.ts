import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideI18nTesting } from '../../../../../../testing/i18n-testing';
import { NoteSeoAnalysis } from '../../../../models/note-seo-analysis';
import { NoteSeoPanelComponent } from './note-seo-panel.component';

describe('NoteSeoPanelComponent', () => {
  let fixture: ComponentFixture<NoteSeoPanelComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NoteSeoPanelComponent],
      providers: [provideI18nTesting()],
    }).compileComponents();

    fixture = TestBed.createComponent(NoteSeoPanelComponent);
    fixture.componentRef.setInput('analysis', analysis());
    fixture.detectChanges();
  });

  it('renders overall status, canonical path, and checks', () => {
    const text = fixture.nativeElement.textContent as string;

    expect(text).toContain('SEO-анализ');
    expect(text).toContain('2 предупреждения');
    expect(text).toContain('/notes/typed-notes');
    expect(text).toContain('Длина заголовка');
    expect(text).toContain('Теги');
  });
});

function analysis(): NoteSeoAnalysis {
  return {
    overallStatus: 'warning',
    canonicalPath: '/notes/typed-notes',
    descriptionPreview:
      'This note explains how typed Angular forms and localized fields work together.',
    goodCount: 1,
    warningCount: 2,
    missingCount: 0,
    checks: [
      {
        id: 'title-present',
        status: 'good',
        titleKey: 'notes.seoAnalysis.check.titlePresent',
        messageKey: 'notes.seoAnalysis.message.titlePresent.good',
      },
      {
        id: 'title-length',
        status: 'warning',
        titleKey: 'notes.seoAnalysis.check.titleLength',
        messageKey: 'notes.seoAnalysis.message.titleLength.warning',
      },
      {
        id: 'active-tags',
        status: 'warning',
        titleKey: 'notes.seoAnalysis.check.activeTags',
        messageKey: 'notes.seoAnalysis.message.activeTags.warning',
      },
    ],
  };
}
