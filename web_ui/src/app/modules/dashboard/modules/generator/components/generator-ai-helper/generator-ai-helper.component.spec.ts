import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GeneratorAiHelperComponent } from './generator-ai-helper.component';

describe('GeneratorAiHelperComponent', () => {
  let component: GeneratorAiHelperComponent;
  let fixture: ComponentFixture<GeneratorAiHelperComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GeneratorAiHelperComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GeneratorAiHelperComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
