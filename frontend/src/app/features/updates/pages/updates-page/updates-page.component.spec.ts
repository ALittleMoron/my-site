import { ComponentFixture, TestBed } from '@angular/core/testing';
import { I18nService } from '../../../../core/i18n/i18n.service';
import { SeoService } from '../../../../core/seo/seo.service';
import { provideI18nTesting } from '../../../../testing/i18n-testing';
import { UpdatesPageComponent } from './updates-page.component';

describe('UpdatesPageComponent', () => {
  let fixture: ComponentFixture<UpdatesPageComponent>;
  let i18n: I18nService;
  let seoService: { setTranslatedMeta: jest.Mock };

  beforeEach(async () => {
    seoService = {
      setTranslatedMeta: jest.fn(),
    };

    await TestBed.configureTestingModule({
      imports: [UpdatesPageComponent],
      providers: [
        provideI18nTesting({
          'updates.seo.title': 'Обновления',
          'updates.seo.description': 'Публичный журнал изменений сайта.',
          'updates.hero.kicker': 'Журнал изменений',
          'updates.hero.title': 'Обновления сайта',
          'updates.hero.lead': 'Крупные изменения сайта и базы знаний, сгруппированные по месяцам.',
          'updates.tag.backend': 'Backend',
          'updates.tag.frontend': 'Frontend',
          'updates.tag.content': 'Контент',
          'updates.tag.seo': 'SEO',
          'updates.tag.analytics': 'Аналитика',
          'updates.tag.matrix': 'Матрица',
          'updates.tag.infra': 'Инфраструктура',
          'updates.tag.admin': 'Админка',
          'updates.tag.auth': 'Auth',
          'updates.tag.localization': 'Локализация',
          'updates.tag.quality': 'Качество',
          'updates.tag.security': 'Безопасность',
          'updates.tag.delivery': 'Доставка',
        }),
        { provide: SeoService, useValue: seoService },
      ],
    }).compileComponents();

    i18n = TestBed.inject(I18nService);
    fixture = TestBed.createComponent(UpdatesPageComponent);
    fixture.detectChanges();
  });

  it('sets localized SEO metadata with canonical alternates', () => {
    expect(seoService.setTranslatedMeta).toHaveBeenCalledWith({
      titleKey: 'updates.seo.title',
      descriptionKey: 'updates.seo.description',
      canonicalPath: '/ru/updates',
      alternates: [
        { language: 'ru', path: '/ru/updates' },
        { language: 'en', path: '/en/updates' },
      ],
    });
  });

  it('renders localized public milestone entries grouped by month', () => {
    const text = fixture.nativeElement.textContent as string;
    const month = fixture.nativeElement.querySelector('time[datetime="2026-07"]');

    expect(text).toContain('Обновления сайта');
    expect(text).toContain('Крупные изменения сайта и базы знаний');
    expect(month?.textContent).toContain('Июль 2026');
    expect(text).toContain('Июнь 2026');
    expect(text).toContain('Сентябрь 2024');
    expect(text).toContain('Релизы и админка стали аккуратнее');
    expect(text).toContain('Публичный SEO-контур вышел в SSR');
    expect(text).toContain('Angular UI заменил прототип');
    expect(text).toContain('Репозиторий стартовал');
    expect(text).toContain('Backend');
    expect(text).toContain('Доставка');
    expect(text).not.toContain('выдуманной');
  });

  it('recomputes authored update content when the language changes', () => {
    i18n.switchLanguage('en').subscribe();
    fixture.detectChanges();

    const text = fixture.nativeElement.textContent as string;
    const month = fixture.nativeElement.querySelector('time[datetime="2026-07"]');

    expect(month?.textContent).toContain('July 2026');
    expect(text).toContain('Release workflow and admin polish');
    expect(text).toContain('Public SEO layer went live');
    expect(text).toContain('Repository started');
    expect(text).not.toContain('Релизы и админка стали аккуратнее');
  });
});
