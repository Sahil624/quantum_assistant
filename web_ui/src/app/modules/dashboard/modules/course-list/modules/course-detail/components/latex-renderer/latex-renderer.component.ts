import { Component, Input, SimpleChanges } from '@angular/core';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';

@Component({
  selector: 'app-latex-renderer',
  standalone: true,
  imports: [],
  template: `
  @if(iframeSrc) {
    <iframe [src]="iframeSrc" width="100%" height="80vh" frameborder="0"></iframe>
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
  iframeSrc!: SafeResourceUrl;

  constructor(private sanitizer: DomSanitizer) {}

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
}
