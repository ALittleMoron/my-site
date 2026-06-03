import { matrixRoutes } from './matrix.routes';

describe('matrixRoutes', () => {
  it('keeps public question pages separate from the overview route', () => {
    expect(matrixRoutes.map((route) => route.path)).toEqual(['questions/:slug', '']);
  });
});
