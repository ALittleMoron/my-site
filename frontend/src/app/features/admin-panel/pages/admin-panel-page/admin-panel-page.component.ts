import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { Router, RouterOutlet } from '@angular/router';
import {
  FoldableTreeComponent,
  FoldableTreeSection,
} from '../../../../shared/ui/foldable-tree/foldable-tree.component';
import { AuthService } from '../../../../core/auth/auth.service';
import { I18nService } from '../../../../core/i18n/i18n.service';
import { TranslatePipe } from '../../../../core/i18n/translate.pipe';
import { ADMIN_PANEL_NAVIGATION_SECTIONS } from '../../admin-panel-navigation';
import { AdminPanelNavigationSection } from '../../models/admin-panel-navigation.model';
import { AdminPanelHeaderComponent } from '../../components/admin-panel-header/admin-panel-header.component';

@Component({
  selector: 'app-admin-panel-page',
  standalone: true,
  imports: [AdminPanelHeaderComponent, FoldableTreeComponent, RouterOutlet, TranslatePipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './admin-panel-page.component.html',
  styleUrl: './admin-panel-page.component.scss',
})
export class AdminPanelPageComponent {
  private readonly auth = inject(AuthService);
  private readonly i18n = inject(I18nService);
  private readonly router = inject(Router);

  readonly sidePanelOpen = signal(true);
  readonly selectedPageKey = signal<string | null>(null);
  readonly visibleNavigationSections = computed<readonly AdminPanelNavigationSection[]>(() => {
    const canManageTeam = this.auth.canManageTeam();
    return ADMIN_PANEL_NAVIGATION_SECTIONS.map((section) => ({
      ...section,
      pages: section.pages.filter((page) => canManageTeam || !page.adminOnly),
    })).filter((section) => section.pages.length > 0);
  });
  readonly defaultExpandedSectionKeys = computed<readonly string[]>(() =>
    this.visibleNavigationSections().map((section) => section.key),
  );
  readonly sidePanelToggleLabel = computed(() =>
    this.i18n.translate(
      this.sidePanelOpen() ? 'adminPanel.sidePanel.close' : 'adminPanel.sidePanel.open',
    ),
  );
  readonly sections = computed<readonly FoldableTreeSection[]>(() => {
    this.i18n.language();
    return this.visibleNavigationSections().map((section) => ({
      key: section.key,
      label: this.i18n.translate(section.labelKey),
      trailingText: String(section.pages.length),
      items: section.pages.map((page) => ({
        key: page.key,
        label: this.i18n.translate(page.labelKey),
        badgeText: page.badgeTextKey === null ? null : this.i18n.translate(page.badgeTextKey),
      })),
    }));
  });

  toggleSidePanel(): void {
    this.sidePanelOpen.update((value) => !value);
  }

  closeSidePanel(): void {
    this.sidePanelOpen.set(false);
  }

  selectPage(pageKey: string): void {
    const page = this.visibleNavigationSections()
      .flatMap((section) => section.pages)
      .find((item) => item.key === pageKey);
    if (!page) return;
    this.selectedPageKey.set(page.key);
    this.closeSidePanel();
    this.router.navigateByUrl(page.route);
  }
}
