import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GeneratorConfirmationComponent } from './generator-confirmation.component';

describe('GeneratorConfirmationComponent', () => {
  let component: GeneratorConfirmationComponent;
  let fixture: ComponentFixture<GeneratorConfirmationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GeneratorConfirmationComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GeneratorConfirmationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
