import { TestBed } from '@angular/core/testing';

import { EhosService } from './ehos.service';

describe('EhosService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: EhosService = TestBed.get(EhosService);
    expect(service).toBeTruthy();
  });
});
