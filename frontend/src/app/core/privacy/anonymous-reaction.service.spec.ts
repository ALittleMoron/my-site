import { TestBed } from '@angular/core/testing';
import { AnonymousReactionService } from './anonymous-reaction.service';

describe('AnonymousReactionService', () => {
  let service: AnonymousReactionService;
  let randomUuid: jest.Mock<string, []>;

  beforeEach(() => {
    localStorage.clear();
    randomUuid = jest.fn().mockReturnValue('generated-token');
    Object.defineProperty(crypto, 'randomUUID', {
      configurable: true,
      value: randomUuid,
    });
    TestBed.configureTestingModule({ providers: [AnonymousReactionService] });
    service = TestBed.inject(AnonymousReactionService);
  });

  afterEach(() => {
    localStorage.clear();
  });

  it('creates client token lazily and reuses it', () => {
    expect(localStorage.getItem('noteReactionClientToken')).toBeNull();

    expect(service.getOrCreateClientToken()).toBe('generated-token');
    expect(service.getOrCreateClientToken()).toBe('generated-token');

    expect(randomUuid).toHaveBeenCalledTimes(1);
    expect(localStorage.getItem('noteReactionClientToken')).toBe('generated-token');
  });

  it('persists and clears note-scoped reaction selection', () => {
    service.setReaction('typed-notes', 'poop');

    expect(service.getReaction('typed-notes')).toBe('poop');

    service.setReaction('typed-notes', null);

    expect(service.getReaction('typed-notes')).toBeNull();
  });
});
