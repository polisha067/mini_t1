import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ContestList } from './contest-list';

describe('ContestList', () => {
  let component: ContestList;
  let fixture: ComponentFixture<ContestList>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ContestList],
    }).compileComponents();

    fixture = TestBed.createComponent(ContestList);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
