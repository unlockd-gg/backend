import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GenericResponseDialogComponent } from './generic-response-dialog.component';

describe('GenericResponseDialogComponent', () => {
  let component: GenericResponseDialogComponent;
  let fixture: ComponentFixture<GenericResponseDialogComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [GenericResponseDialogComponent]
    });
    fixture = TestBed.createComponent(GenericResponseDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
