import { Component, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';

@Component({
  selector: 'app-generic-response-dialog',
  templateUrl: './generic-response-dialog.component.html',
  styleUrls: ['./generic-response-dialog.component.css']
})
export class GenericResponseDialogComponent {
  constructor(
    public dialogRef: MatDialogRef<GenericResponseDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any) { }
  
  onCancel(): void {
    this.dialogRef.close();
  }
}
