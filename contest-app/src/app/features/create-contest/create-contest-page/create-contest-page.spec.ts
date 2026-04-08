import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreateContestPage } from './create-contest-page';

describe('CreateContestPage', () => {
  let component: CreateContestPage;
  let fixture: ComponentFixture<CreateContestPage>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CreateContestPage],
    }).compileComponents();

    fixture = TestBed.createComponent(CreateContestPage);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
