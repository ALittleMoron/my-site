interface AngularWorkspace {
  projects: Record<string, AngularProject>;
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
});

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
