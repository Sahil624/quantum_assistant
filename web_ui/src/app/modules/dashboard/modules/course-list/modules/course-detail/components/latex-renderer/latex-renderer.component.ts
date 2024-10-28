import { Component, Input, SimpleChanges } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { CourseService } from '../../../../../../../../helpers/services/course/course.service';

@Component({
  selector: 'app-latex-renderer',
  standalone: true,
  imports: [
    MatButtonModule
  ],
  template: `
  @if(iframeSrc) {
    <iframe [src]="iframeSrc" width="100%" height="80vh" frameborder="0"></iframe>
  }

  @if(quizCell) {
    <button mat-flat-button (click)="downloadFile()">Download Quiz Notebook!</button>
  }
  `,
  styles: `
  iframe {
    height: 80vh
  }
  `
})
export class LatexRendererComponent {
  @Input() htmlContent!: string;
  @Input() quizCell!: string;
  downloading = false;
  error: string | null = null;
  iframeSrc!: SafeResourceUrl;

  constructor(
    private sanitizer: DomSanitizer,
    private courseService: CourseService
  ) {}

  ngOnChanges(changes: SimpleChanges) {
    if (changes['htmlContent']) {
      this.updateIframeSrc();
    }
  }


  private updateIframeSrc() {
    const fullHtml = `
      <!DOCTYPE html>
      <html>
        <head>
          <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
          <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
        </head>
        <body>
          ${this.htmlContent}
          <script>
            MathJax = {
              tex: {
                inlineMath: [['$', '$'], ['\\(', '\\)']]
              },
              startup: {
                pageReady: () => {
                  return MathJax.startup.defaultPageReady().then(() => {
                    console.log('MathJax initial typesetting complete');
                  });
                }
              }
            };
          </script>
        </body>
      </html>
    `;

    const blob = new Blob([this.htmlContent], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    this.iframeSrc = this.sanitizer.bypassSecurityTrustResourceUrl(url);
  }

  downloadFile(): void {
    this.downloading = true;
    this.error = null;

    this.courseService.downloadFile(this.quizCell).subscribe({
      next: (blob: Blob) => {
        // Create URL and trigger download
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = this.quizCell + ".ipynb";
        
        // Append to body, click, and clean up
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        
        this.downloading = false;
      },
      error: (error: Error) => {
        this.error = error.message;
        this.downloading = false;
      }
    });
  }
}
