import { CanActivateFn } from '@angular/router';

// Stub: always allows access. Replace with PASETO token validation when auth is implemented.
export const authGuard: CanActivateFn = () => true;
