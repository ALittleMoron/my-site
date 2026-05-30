import { ChangeDetectionStrategy, Component, OnInit, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { TranslatePipe } from '../../../../core/i18n/translate.pipe';
import { SeoService } from '../../../../core/seo/seo.service';

@Component({
  selector: 'app-not-found-page',
  standalone: true,
  imports: [RouterLink, TranslatePipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './not-found-page.component.html',
})
export class NotFoundPageComponent implements OnInit {
  private readonly seoService = inject(SeoService);

  ngOnInit(): void {
    this.seoService.setTranslatedMeta({
      titleKey: 'notFound.seo.title',
      descriptionKey: 'notFound.seo.description',
    });
  }
}
