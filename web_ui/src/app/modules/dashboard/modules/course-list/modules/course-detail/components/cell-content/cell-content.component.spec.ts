import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CellContentComponent } from './cell-content.component';

describe('CellContentComponent', () => {
  let component: CellContentComponent;
  let fixture: ComponentFixture<CellContentComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CellContentComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CellContentComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
