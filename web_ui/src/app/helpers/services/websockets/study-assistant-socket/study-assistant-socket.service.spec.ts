import { TestBed } from '@angular/core/testing';

import { StudyAssistantSocketService } from './study-assistant-socket.service';

describe('StudyAssistantSocketService', () => {
  let service: StudyAssistantSocketService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(StudyAssistantSocketService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
