import { NgClass } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormControl, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatDialogRef } from '@angular/material/dialog';
import { MatDividerModule } from '@angular/material/divider';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { ConversationMessageI } from '../../services/websockets/study-assistant-socket/study-assistant.interface';

@Component({
  selector: 'app-chat-conversation',
  standalone: true,
  imports: [
    MatIconModule,
    MatButtonModule,
    NgClass,
    MatDividerModule,
    MatInputModule,
    MatFormFieldModule,
    FormsModule,
    ReactiveFormsModule
  ],
  templateUrl: './chat-conversation.component.html',
  styleUrl: './chat-conversation.component.scss'
})
export class ChatConversationComponent {
  @Input() title!: string;
  @Input() description!: string;
  @Input() conversation: ConversationMessageI[] = [];
  @Output() queryEvent = new EventEmitter<string>();

  chatInput = new FormControl();

  // conversation = [
  //   {
  //     from: 'system',
  //     message: 'How can I help you?'
  //   },
  //   {
  //     from: 'user',
  //     message: 'What is qbit?'
  //   },
  //   {
  //     from: 'system',
  //     message: 'Here is definition of qbit.'
  //   },
  // ]

  constructor(
    private dialogRef: MatDialogRef<ChatConversationComponent>
  ) { }

  close() {
    this.dialogRef.close();
  }

  emitMessage() {
    if (this.chatInput.value) {
      this.queryEvent.emit(this.chatInput.value);
      this.chatInput.reset();
    }
  }
}
