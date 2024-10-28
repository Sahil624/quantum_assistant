import { Component, Input, OnInit, ViewChild } from '@angular/core';
import { AvailableLOResponse } from '../../../../../../helpers/services/course/course.interface';
import { MatTree, MatTreeModule } from '@angular/material/tree';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { SelectionModel } from '@angular/cdk/collections';

interface treeInterface {
  name: string;
  id: string;
  children: treeInterface[];
}

@Component({
  selector: 'app-lo-tree',
  standalone: true,
  imports: [
    MatTreeModule,
    MatButtonModule,
    MatIconModule,
    MatCheckboxModule
  ],
  templateUrl: './lo-tree.component.html',
  styleUrl: './lo-tree.component.scss'
})
export class LoTreeComponent implements OnInit {
  @Input() availableCourses!: AvailableLOResponse;
  @Input() unit!: string;
  @ViewChild(MatTree) treeControl!: MatTree<treeInterface>;
  dataset: treeInterface[] = [];
  selectedLOs = 0;
  childrenAccessor = (node: treeInterface) => node?.children ?? [];
  hasChild = (_: number, node: treeInterface) => node?.children?.length > 0;
  checklistSelection = new SelectionModel<treeInterface>(true /* multiple */);



  ngOnInit(): void {
    this.dataset = Object.keys(this.availableCourses[this.unit]).map(topic => {
      const node: treeInterface = {
        id: this.formatId(this.unit, topic, ''),
        name: topic,
        children: this.availableCourses[this.unit][topic].outcomes.map((x) => {
          return {
            id: this.formatId(this.unit, topic, x.outcome),
            children: [],
            name: x.outcome
          }
        })
      }
      return node
    });
  }

  /** Whether all the descendants of the node are selected */
  descendantsAllSelected(node: treeInterface): boolean {
    const descendants = this.childrenAccessor(node);

    this.updateSelectedCount();
    return descendants.every(child => this.checklistSelection.isSelected(child));
  }

  /** Whether part of the descendants are selected */
  descendantsPartiallySelected(node: treeInterface): boolean {
    const descendants = this.childrenAccessor(node);
    const result = descendants.some(child => this.checklistSelection.isSelected(child));

    this.updateSelectedCount();
    return result && !this.descendantsAllSelected(node);
  }

  /** Toggle the to-do item selection. Select/deselect all the descendants node */
  todoItemSelectionToggle(node: treeInterface): void {
    this.checklistSelection.toggle(node);
    const descendants = this.childrenAccessor(node);
    this.checklistSelection.isSelected(node)
      ? this.checklistSelection.select(...descendants)
      : this.checklistSelection.deselect(...descendants);

    this.updateSelectedCount();
  }

  getSelectedOutcomes() {
    const selectedOuts: string[][] = [];
    this.checklistSelection.selected.forEach((node) => {
      const parsed = this.parseObjectID(node.id);

      if (parsed[2] != '') {
        selectedOuts.push(parsed);
      }
    });

    return selectedOuts;
  }

  updateSelectedCount() {
    this.selectedLOs = this.getSelectedOutcomes().length;
  }


  formatId(unit: string, topic: string, name: string) {
    return unit + '__' + topic + '__' + name;
  }

  parseObjectID(id: string) {
    return id.split('__');
  }

}
