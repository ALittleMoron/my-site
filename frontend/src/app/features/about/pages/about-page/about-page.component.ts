import { ChangeDetectionStrategy, Component, OnInit, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { TranslatePipe } from '../../../../core/i18n/translate.pipe';
import { SeoService } from '../../../../core/seo/seo.service';

@Component({
  selector: 'app-about-page',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [RouterLink, TranslatePipe],
  templateUrl: './about-page.component.html',
})
export class AboutPageComponent implements OnInit {
  private readonly seoService = inject(SeoService);

  ngOnInit(): void {
    this.seoService.setTranslatedMeta({
      titleKey: 'about.seo.title',
      descriptionKey: 'about.seo.description',
      canonicalPath: '/about-me',
    });
  }
}
