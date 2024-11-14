import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'moduleNameFormatter',
  standalone: true
})
export class ModuleNameFormatterPipe implements PipeTransform {

  convertToReadableString(input: string): string {
    // Handle quiz patterns first
    const quizInteractivePattern = /m(\d+)-quiz-(\d+)\.(\d+)-interactive\./;
    const quizPattern = /m(\d+)-quiz-(\d+)\.(\d+)/;

    // Check for interactive quiz pattern
    if (quizInteractivePattern.test(input)) {
      const matches = input.match(quizInteractivePattern);
      if (matches) {
        return `Self Assessment Quiz ${matches[3]} Interactive`;
      }
    }

    // Check for regular quiz pattern
    if (quizPattern.test(input)) {
      const matches = input.match(quizPattern);
      if (matches) {
        return `Self Assessment Quiz ${matches[3]}`;
      }
    }

    // Handle general cases
    // Remove module number prefix (e.g., 'm10-')
    let processed = input.replace(/^m\d+-/, '');

    // Remove trailing period if exists
    processed = processed.replace(/\.$/, '');

    // Split by hyphens
    const words = processed.split('-');

    // Capitalize first letter of each word and join with spaces
    return words
      .map(word => {
        // Handle camelCase words (e.g., LinearCombination)
        return word.replace(/([A-Z])/g, ' $1')
          .trim() // Remove any leading/trailing spaces
          .split(' ') // Split into words
          .map(part => part.charAt(0).toUpperCase() + part.slice(1).toLowerCase())
          .join(' ');
      })
      .join(' ');
  }

  transform(value: string, moduleName?: string): string {
    if (moduleName) {
      return moduleName
    }

    return this.convertToReadableString(value);
  }

}
