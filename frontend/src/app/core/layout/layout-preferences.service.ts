import { DOCUMENT } from '@angular/common';
import { Injectable, inject, signal } from '@angular/core';

export type MatrixLayoutMode = 'list' | 'grid';

const STORAGE_KEY = 'chosenLayout';

@Injectable({ providedIn: 'root' })
export class LayoutPreferencesService {
  private readonly document = inject(DOCUMENT);

  readonly matrixLayout = signal<MatrixLayoutMode>(this.readInitialLayout());

  setMatrixLayout(layout: MatrixLayoutMode): void {
    this.storage()?.setItem(STORAGE_KEY, layout);
    this.matrixLayout.set(layout);
  }

  private readInitialLayout(): MatrixLayoutMode {
    const value = this.storage()?.getItem(STORAGE_KEY);
    return value === 'grid' || value === 'list' ? value : 'list';
  }

  private storage(): Storage | null {
    return this.document.defaultView?.localStorage ?? null;
  }
}
