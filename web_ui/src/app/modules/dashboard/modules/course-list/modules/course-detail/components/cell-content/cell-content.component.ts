import { Component, Input } from '@angular/core';
import { CourseService } from '../../../../../../../../helpers/services/course/course.service';
import { CellDataResponse } from '../../../../../../../../helpers/services/course/course.interface';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { LatexRendererComponent } from '../latex-renderer/latex-renderer.component';

@Component({
  selector: 'app-cell-content',
  standalone: true,
  imports: [
    LatexRendererComponent
  ],
  templateUrl: './cell-content.component.html',
  styleUrl: './cell-content.component.scss'
})
export class CellContentComponent {
  private _cellID!: string;
  public get cellID(): string {
    return this._cellID;
  }
  
  @Input()
  public set cellID(value: string) {
    const isChanged = value != this._cellID;
    this._cellID = value;

    if(isChanged) {
      this.fetchCellID();
    }
  }

  cellDataResponse !: CellDataResponse;
  content!: SafeHtml;

  constructor(
    private courseService: CourseService,
    private sanitizer: DomSanitizer
  ) {
  }


  fetchCellID() {
    this.courseService.fetchCellData(this.cellID).subscribe((res) => {
      this.cellDataResponse = res;
      this.content = this.sanitizer.bypassSecurityTrustHtml(res.content);
    });
  }
}
