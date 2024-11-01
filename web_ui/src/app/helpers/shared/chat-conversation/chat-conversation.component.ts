import { NgClass } from '@angular/common';
import { Component, ElementRef, EventEmitter, Input, OnChanges, OnInit, Output, SimpleChanges, ViewChild } from '@angular/core';
import { FormControl, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatDialogRef } from '@angular/material/dialog';
import { MatDividerModule } from '@angular/material/divider';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MessageType } from '../../services/conversation/conversation.enums';
import { MessageI } from '../../services/conversation/conversation.interface';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatTooltipModule } from '@angular/material/tooltip';

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
    ReactiveFormsModule,
    MatProgressSpinnerModule,
    MatTooltipModule
  ],
  templateUrl: './chat-conversation.component.html',
  styleUrl: './chat-conversation.component.scss'
})
export class ChatConversationComponent implements OnInit, OnChanges {
  @Input() title!: string;
  @Input() description!: string;
  @Input() conversation: MessageI[] = [];
  @Input() messageUpdated!: EventEmitter<any>;
  @Input() thinking: boolean = false;
  @Output() queryEvent = new EventEmitter<string>();
  @Output() enableExternalSourceEvent = new EventEmitter<boolean>();
  @ViewChild('chatScroll') chatScroll!: ElementRef;
  showExternalDataConfirmation = false;

  externalHint = "External sources were used for this conversation";

  chatInput = new FormControl();
  MessageType = MessageType;

  constructor(
    private dialogRef: MatDialogRef<ChatConversationComponent>,
    private snackbar: MatSnackBar
  ) {
  }

  ngOnInit(): void {
    this.messageUpdated.subscribe(() => {
      setTimeout(() => {
        this.scrollToBottom();
      }, 100);
      this.scrollToBottom();
    })
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['conversation']) {
      // this.checkExternalMessageConfirmation();
    }
  }

  close() {
    this.dialogRef.close();
  }

  emitMessage(message?: string) {
    message = this.chatInput.value || message;

    if (this.thinking) {
      this.snackbar.open('Please wait for previous query to be processed.');
      return;
    }

    if (this.showExternalDataConfirmation) {
      this.snackbar.open('Please confirm last message');
      return;
    }

    if (message) {
      this.queryEvent.emit(message);
      this.chatInput.reset();
      this.scrollToBottom();
    }
  }

  searchExternalSources() {
    this.showExternalDataConfirmation = false;
    this.enableExternalSourceEvent.emit(true);
    this.emitMessage('Answer from external sources.');
  }

  scrollToBottom() {
    if (!this.chatScroll) {
      console.log('Chat Element Not Found');
      return;
    }
    this.chatScroll.nativeElement.scrollTo(0, this.chatScroll.nativeElement.scrollHeight);

    this.checkExternalMessageConfirmation();
  }

  checkExternalMessageConfirmation() {
    if (!this.conversation) { return; }
    this.showExternalDataConfirmation = this.conversation[this.conversation.length - 1]?.is_out_of_context_message || false;
  }
}
