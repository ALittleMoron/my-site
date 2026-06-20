export interface AdminPanelNavigationPage {
  key: string;
  labelKey: string;
  route: string;
  badgeTextKey: string | null;
  adminOnly: boolean;
}

export interface AdminPanelNavigationSection {
  key: string;
  labelKey: string;
  pages: readonly AdminPanelNavigationPage[];
}
