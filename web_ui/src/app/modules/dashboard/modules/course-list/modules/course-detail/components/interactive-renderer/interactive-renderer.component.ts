import { Component, Input, SimpleChanges } from '@angular/core';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';

@Component({
  selector: 'app-interactive-renderer',
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
export class InteractiveRendererComponent {
  @Input() interactiveUrl!: string;
  iframeSrc!: SafeResourceUrl;

  constructor(private sanitizer: DomSanitizer) { }

  ngOnChanges(changes: SimpleChanges) {
    if (changes['interactiveUrl']) {
      this.updateIframeSrc();
    }
  }

  updateIframeSrc() {
    this.iframeSrc = this.sanitizer.bypassSecurityTrustResourceUrl(this.interactiveUrl);
  }
}
