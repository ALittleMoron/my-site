import { ChangeDetectionStrategy, Component, input } from '@angular/core';
import { I18nParams } from '../../../../../../core/i18n/i18n.model';
import { TranslatePipe } from '../../../../../../core/i18n/translate.pipe';
import { NoteSeoAnalysis, NoteSeoStatus } from '../../../../models/note-seo-analysis';

@Component({
  selector: 'app-note-seo-panel',
  standalone: true,
  imports: [TranslatePipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './note-seo-panel.component.html',
})
export class NoteSeoPanelComponent {
  readonly analysis = input.required<NoteSeoAnalysis>();

  summaryKey(): string {
    return `notes.seoAnalysis.summary.${this.analysis().overallStatus}`;
  }

  summaryParams(): I18nParams {
    const analysis = this.analysis();
    return {
      good: analysis.goodCount,
      warning: analysis.warningCount,
      missing: analysis.missingCount,
      count: analysis.overallStatus === 'missing' ? analysis.missingCount : analysis.warningCount,
    };
  }

  statusKey(status: NoteSeoStatus): string {
    return `notes.seoAnalysis.status.${status}`;
  }

  statusClass(status: NoteSeoStatus): string {
    if (status === 'good') return 'badge text-bg-success';
    if (status === 'warning') return 'badge text-bg-warning';
    return 'badge text-bg-danger';
  }
}
