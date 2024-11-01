import { ComponentFixture, TestBed } from '@angular/core/testing';

import { InteractiveRendererComponent } from './interactive-renderer.component';

describe('InteractiveRendererComponent', () => {
  let component: InteractiveRendererComponent;
  let fixture: ComponentFixture<InteractiveRendererComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [InteractiveRendererComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(InteractiveRendererComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
