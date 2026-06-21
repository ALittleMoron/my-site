interface AngularWorkspace {
  projects: Record<string, AngularProject>;
}

interface FileSystemModule {
  readFileSync(path: string, encoding: 'utf8'): string;
}

interface AngularProject {
  architect?: {
    build?: {
      options?: {
        styles?: readonly AngularStyleEntry[];
      };
    };
  };
}

type AngularStyleEntry = string | { input?: string; inject?: boolean; bundleName?: string };

declare const require: (path: string) => unknown;

const fileSystem = require('node:fs') as FileSystemModule;

describe('Angular build styles', () => {
  it('keeps Toast UI editor CSS out of the global initial stylesheet', () => {
    const workspace = readAngularWorkspace();
    const styles = workspace.projects['my-site-frontend']?.architect?.build?.options?.styles ?? [];
    const injectedStyles = styles.filter(isInjectedStyle).map(readStylePath);

    expect(injectedStyles).toEqual(['src/styles/main.scss']);
    expect(findStyle(styles, 'node_modules/@toast-ui/editor/dist/toastui-editor.css')).toEqual({
      input: 'node_modules/@toast-ui/editor/dist/toastui-editor.css',
      inject: false,
      bundleName: 'toastui-editor',
    });
    expect(
      findStyle(styles, 'node_modules/@toast-ui/editor/dist/theme/toastui-editor-dark.css'),
    ).toEqual({
      input: 'node_modules/@toast-ui/editor/dist/theme/toastui-editor-dark.css',
      inject: false,
      bundleName: 'toastui-editor-dark',
    });
  });

  it('keeps primary buttons on dedicated high-contrast theme tokens', () => {
    const themeStyles = readStyleFile('src/styles/_theme.scss');
    const componentStyles = readStyleFile('src/styles/_components.scss');
    const lightButtonText = readCssVariable(themeStyles, 'button-primary-color', 'light');
    const lightButtonBackground = readCssVariable(themeStyles, 'button-primary-bg', 'light');
    const darkButtonText = readCssVariable(themeStyles, 'button-primary-color', 'dark');
    const darkButtonBackground = readCssVariable(themeStyles, 'button-primary-bg', 'dark');
    const lightSurface = readCssVariable(themeStyles, 'main-bg-color', 'light');
    const darkSurface = readCssVariable(themeStyles, 'main-bg-color', 'dark');
    const lightReadableLink = readCssVariable(themeStyles, 'link-readable-color', 'light');
    const darkReadableLink = readCssVariable(themeStyles, 'link-readable-color', 'dark');
    const lightOutlineSecondary = readCssVariable(themeStyles, 'outline-secondary-color', 'light');
    const darkOutlineSecondary = readCssVariable(themeStyles, 'outline-secondary-color', 'dark');

    expect(componentStyles).toContain('--bs-btn-color: var(--button-primary-color);');
    expect(componentStyles).toContain('--bs-btn-bg: var(--button-primary-bg);');
    expect(componentStyles).toContain('--bs-btn-hover-bg: var(--button-primary-hover-bg);');
    expect(componentStyles).toContain('color: var(--button-primary-color) !important;');
    expect(componentStyles).toContain('background-color: var(--button-primary-bg) !important;');
    expect(componentStyles).toContain(
      'background-color: var(--button-primary-hover-bg) !important;',
    );
    expect(componentStyles).toContain('--bs-btn-color: var(--outline-secondary-color);');
    expect(componentStyles).toContain('color: var(--link-readable-color) !important;');
    expect(contrastRatio(lightButtonText, lightButtonBackground)).toBeGreaterThanOrEqual(4.5);
    expect(contrastRatio(darkButtonText, darkButtonBackground)).toBeGreaterThanOrEqual(4.5);
    expect(contrastRatio(lightReadableLink, lightSurface)).toBeGreaterThanOrEqual(4.5);
    expect(contrastRatio(darkReadableLink, darkSurface)).toBeGreaterThanOrEqual(4.5);
    expect(contrastRatio(lightOutlineSecondary, lightSurface)).toBeGreaterThanOrEqual(4.5);
    expect(contrastRatio(darkOutlineSecondary, darkSurface)).toBeGreaterThanOrEqual(4.5);
  });
});

function readStyleFile(path: string): string {
  return fileSystem.readFileSync(path, 'utf8');
}

function readCssVariable(styles: string, name: string, theme: 'light' | 'dark'): string {
  const themeBlock = extractThemeBlock(styles, theme);
  const match = themeBlock.match(new RegExp(`--${name}:\\s*(rgb\\([^)]+\\));`));
  if (!match) {
    throw new Error(`Missing --${name} in ${theme} theme.`);
  }
  return match[1];
}

function extractThemeBlock(styles: string, theme: 'light' | 'dark'): string {
  const start = styles.indexOf(`:root[data-bs-theme='${theme}']`);
  if (start < 0) {
    throw new Error(`Missing ${theme} theme block.`);
  }
  const nextTheme = styles.indexOf(":root[data-bs-theme='", start + 1);
  return nextTheme < 0 ? styles.slice(start) : styles.slice(start, nextTheme);
}

function contrastRatio(foreground: string, background: string): number {
  const foregroundLuminance = relativeLuminance(parseRgb(foreground));
  const backgroundLuminance = relativeLuminance(parseRgb(background));
  const lighter = Math.max(foregroundLuminance, backgroundLuminance);
  const darker = Math.min(foregroundLuminance, backgroundLuminance);
  return (lighter + 0.05) / (darker + 0.05);
}

function parseRgb(value: string): readonly [number, number, number] {
  const match = value.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);
  if (!match) {
    throw new Error(`Expected rgb() color, got ${value}.`);
  }
  return [Number(match[1]), Number(match[2]), Number(match[3])];
}

function relativeLuminance([red, green, blue]: readonly [number, number, number]): number {
  const [linearRed, linearGreen, linearBlue] = [red, green, blue].map(linearizeColor);
  return 0.2126 * linearRed + 0.7152 * linearGreen + 0.0722 * linearBlue;
}

function linearizeColor(value: number): number {
  const channel = value / 255;
  return channel <= 0.03928 ? channel / 12.92 : ((channel + 0.055) / 1.055) ** 2.4;
}

function readAngularWorkspace(): AngularWorkspace {
  const workspace = require('../angular.json');
  if (!isAngularWorkspace(workspace)) {
    throw new Error('angular.json does not match the expected Angular workspace shape.');
  }
  return workspace;
}

function readStylePath(style: AngularStyleEntry): string {
  return typeof style === 'string' ? style : (style.input ?? '');
}

function isInjectedStyle(style: AngularStyleEntry): boolean {
  return typeof style === 'string' || style.inject !== false;
}

function findStyle(
  styles: readonly AngularStyleEntry[],
  input: string,
): { input?: string; inject?: boolean; bundleName?: string } | null {
  const match = styles.find((style) => typeof style !== 'string' && style.input === input);
  return typeof match === 'string' || match === undefined ? null : match;
}

function isAngularWorkspace(value: unknown): value is AngularWorkspace {
  if (!isRecord(value)) return false;
  return isRecord(value['projects']);
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null;
}
