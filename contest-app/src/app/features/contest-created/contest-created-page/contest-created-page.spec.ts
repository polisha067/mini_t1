import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ContestCreatedPage } from './contest-created-page';

describe('ContestCreatedPage', () => {
  let component: ContestCreatedPage;
  let fixture: ComponentFixture<ContestCreatedPage>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ContestCreatedPage],
    }).compileComponents();

    fixture = TestBed.createComponent(ContestCreatedPage);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
