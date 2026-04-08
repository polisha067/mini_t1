import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ParticipantsPage } from './participants-page';

describe('ParticipantsPage', () => {
  let component: ParticipantsPage;
  let fixture: ComponentFixture<ParticipantsPage>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ParticipantsPage],
    }).compileComponents();

    fixture = TestBed.createComponent(ParticipantsPage);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
