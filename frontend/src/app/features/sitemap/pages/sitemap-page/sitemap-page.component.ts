import { ChangeDetectionStrategy, Component, OnInit, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { SeoService } from '../../../../core/seo/seo.service';

@Component({
  selector: 'app-sitemap-page',
  standalone: true,
  imports: [RouterLink],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './sitemap-page.component.html',
})
export class SitemapPageComponent implements OnInit {
  private readonly seoService = inject(SeoService);

  ngOnInit(): void {
    this.seoService.setMeta({
      title: 'Карта сайта',
      description: 'Карта сайта.',
    });
  }
}
