import { Injectable, signal } from '@angular/core';

export type MatrixLayoutMode = 'list' | 'grid';

const STORAGE_KEY = 'chosenLayout';

@Injectable({ providedIn: 'root' })
export class LayoutPreferencesService {
  readonly matrixLayout = signal<MatrixLayoutMode>(this.readInitialLayout());

  setMatrixLayout(layout: MatrixLayoutMode): void {
    localStorage.setItem(STORAGE_KEY, layout);
    this.matrixLayout.set(layout);
  }

  private readInitialLayout(): MatrixLayoutMode {
    const value = localStorage.getItem(STORAGE_KEY);
    return value === 'grid' || value === 'list' ? value : 'list';
  }
}
