import { Component, EventEmitter, inject } from '@angular/core';
import { ChatConversationComponent } from '../chat-conversation/chat-conversation.component';
import { ConversationService } from '../../services/conversation/conversation.service';
import { AssistantType, MessageType } from '../../services/conversation/conversation.enums';
import { MessageI } from '../../services/conversation/conversation.interface';
import { ActivityService } from '../../services/activity/activity.service';
import { ActivityType } from '../../services/activity/activity.enums';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { AskQuestionDetails } from '../../services/activity/activity.interface';

@Component({
  selector: 'app-ai-assistant',
  standalone: true,
  imports: [
    ChatConversationComponent
  ],
  templateUrl: './ai-assistant.component.html',
  styleUrl: './ai-assistant.component.scss'
})
export class AiAssistantComponent {
  readonly modelData = inject(MAT_DIALOG_DATA);
  conversationID: string | null = null;
  conversation: MessageI[] = [];
  messageUpdated = new EventEmitter<any>();
  thinking = false;
  enableExternalSource = false;

  constructor(
    private conversationService: ConversationService,
    private activityService: ActivityService
  ) {
    if (this.conversationID) {
      this.getConversation();
    }
  }

  startConversation(pendingMessage?: string) {
    this.conversationService.startConversations(pendingMessage || '', AssistantType.STUDY).subscribe((res) => {
      this.conversationID = res.id.toString();

      if (pendingMessage) {
        this.recordQuestionActivity();
        this.sendMessage(pendingMessage, true);
      }
    })
  }

  sendMessage(message: string, forceSend = false) {
    if (this.thinking && !forceSend) { return; }
    this.thinking = true;
    const tempMessage: MessageI = {
      content: '',
      entities: {
        user_query: message
      },
      id: -1,
      is_answer: false,
      message_type: MessageType.USER,
      is_original_user_query: true,
      is_out_of_context_message: this.enableExternalSource,
      timestamp: Date.now().toString()
    };
    this.conversation.push(tempMessage);
    this.messageUpdated.emit();

    if (!this.conversationID) { this.startConversation(message); }
    else {
      this.conversationService.askQuery(this.conversationID, message, this.enableExternalSource).subscribe((messages) => {
        this.conversation.pop();
        this.conversation = this.conversation.concat(messages);
        this.messageUpdated.emit();
        this.thinking = false;
      })
    }
  }

  getConversation() {
    if (!this.conversationID) { return; }
    this.conversationService.getConversation(this.conversationID).subscribe((res) => {
      this.conversation = res.messages;
      this.messageUpdated.emit();
    })
  }

  recordQuestionActivity() {
    if (!this.conversationID) { return; }
    const courseID = this.modelData['courseId'];
    const activeLo = this.modelData['lo'];

    const details: AskQuestionDetails = {
      conversation_id: +this.conversationID,
      first_question: this.conversation[0].entities['user_query'],
      lo_opened: activeLo
    }

    this.activityService.saveActivity({
      activity_type: ActivityType.AskQuestion,
      course: courseID,
      details
    }).subscribe();
  }
}
