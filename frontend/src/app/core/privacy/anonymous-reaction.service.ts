import { Injectable } from '@angular/core';

const CLIENT_TOKEN_KEY = 'noteReactionClientToken';
const REACTION_SELECTIONS_KEY = 'noteReactionSelections';

@Injectable({ providedIn: 'root' })
export class AnonymousReactionService {
  getOrCreateClientToken(): string {
    const existingToken = localStorage.getItem(CLIENT_TOKEN_KEY);
    if (existingToken) {
      return existingToken;
    }
    const token = crypto.randomUUID();
    localStorage.setItem(CLIENT_TOKEN_KEY, token);
    return token;
  }

  getReaction(slug: string): string | null {
    return this.readSelections()[slug] ?? null;
  }

  setReaction(slug: string, reactionKind: string | null): void {
    const selections = this.readSelections();
    if (reactionKind === null) {
      delete selections[slug];
    } else {
      selections[slug] = reactionKind;
    }
    localStorage.setItem(REACTION_SELECTIONS_KEY, JSON.stringify(selections));
  }

  private readSelections(): Record<string, string> {
    const rawValue = localStorage.getItem(REACTION_SELECTIONS_KEY);
    if (!rawValue) {
      return {};
    }
    let parsedValue: unknown;
    try {
      parsedValue = JSON.parse(rawValue);
    } catch {
      return {};
    }
    if (!isStringRecord(parsedValue)) {
      return {};
    }
    return parsedValue;
  }
}

function isStringRecord(value: unknown): value is Record<string, string> {
  return (
    typeof value === 'object' &&
    value !== null &&
    Object.values(value).every((entry) => typeof entry === 'string')
  );
}
