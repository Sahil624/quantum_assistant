import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LoTreeComponent } from './lo-tree.component';

describe('LoTreeComponent', () => {
  let component: LoTreeComponent;
  let fixture: ComponentFixture<LoTreeComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LoTreeComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(LoTreeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
