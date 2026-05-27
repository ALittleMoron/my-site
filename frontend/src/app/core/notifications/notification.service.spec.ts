import { TestBed } from '@angular/core/testing';
import { NotificationService } from './notification.service';

describe('NotificationService', () => {
  let service: NotificationService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(NotificationService);
  });

  it('adds success and error notifications', () => {
    service.success('Saved');
    service.error('Failed');

    expect(service.notifications()).toEqual([
      { id: 1, type: 'success', message: 'Saved' },
      { id: 2, type: 'danger', message: 'Failed' },
    ]);
  });

  it('dismisses notification by id', () => {
    service.success('Saved');
    service.error('Failed');

    service.dismiss(1);

    expect(service.notifications()).toEqual([{ id: 2, type: 'danger', message: 'Failed' }]);
  });
});
