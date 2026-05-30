import { ChangeDetectionStrategy, Component, OnInit, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { TranslatePipe } from '../../../../core/i18n/translate.pipe';
import { SeoService } from '../../../../core/seo/seo.service';

@Component({
  selector: 'app-sitemap-page',
  standalone: true,
  imports: [RouterLink, TranslatePipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './sitemap-page.component.html',
})
export class SitemapPageComponent implements OnInit {
  private readonly seoService = inject(SeoService);

  ngOnInit(): void {
    this.seoService.setTranslatedMeta({
      titleKey: 'sitemap.seo.title',
      descriptionKey: 'sitemap.seo.description',
      canonicalPath: '/sitemap',
    });
  }
}
