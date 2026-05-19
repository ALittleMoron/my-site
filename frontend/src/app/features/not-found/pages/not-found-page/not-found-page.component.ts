import { ChangeDetectionStrategy, Component, OnInit, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { SeoService } from '../../../../core/seo/seo.service';

@Component({
  selector: 'app-not-found-page',
  standalone: true,
  imports: [RouterLink],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './not-found-page.component.html',
})
export class NotFoundPageComponent implements OnInit {
  private readonly seoService = inject(SeoService);

  ngOnInit(): void {
    this.seoService.setMeta({
      title: '404',
      description: 'Страница не найдена.',
    });
  }
}
