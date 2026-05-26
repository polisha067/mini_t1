import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EditContestPage } from './edit-contest-page';

describe('EditContestPage', () => {
  let component: EditContestPage;
  let fixture: ComponentFixture<EditContestPage>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EditContestPage],
    }).compileComponents();

    fixture = TestBed.createComponent(EditContestPage);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});