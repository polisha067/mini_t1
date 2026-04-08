import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ContestDetailsPage } from './contest-details-page';

describe('ContestDetailsPage', () => {
  let component: ContestDetailsPage;
  let fixture: ComponentFixture<ContestDetailsPage>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ContestDetailsPage],
    }).compileComponents();

    fixture = TestBed.createComponent(ContestDetailsPage);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
