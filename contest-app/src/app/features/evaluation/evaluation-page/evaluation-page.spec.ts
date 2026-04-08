import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EvaluationPage } from './evaluation-page';

describe('EvaluationPage', () => {
  let component: EvaluationPage;
  let fixture: ComponentFixture<EvaluationPage>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EvaluationPage],
    }).compileComponents();

    fixture = TestBed.createComponent(EvaluationPage);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
