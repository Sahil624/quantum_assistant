import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LatexRendererComponent } from './latex-renderer.component';

describe('LatexRendererComponent', () => {
  let component: LatexRendererComponent;
  let fixture: ComponentFixture<LatexRendererComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LatexRendererComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(LatexRendererComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
