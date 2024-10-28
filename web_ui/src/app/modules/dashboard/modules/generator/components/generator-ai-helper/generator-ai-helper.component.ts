import { Component, EventEmitter, inject } from '@angular/core';
import { ChatConversationComponent } from '../../../../../../helpers/shared/chat-conversation/chat-conversation.component';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MessageI } from '../../../../../../helpers/services/conversation/conversation.interface';
import { ConversationService } from '../../../../../../helpers/services/conversation/conversation.service';
import { ActivityService } from '../../../../../../helpers/services/activity/activity.service';
import { AssistantType, MessageType } from '../../../../../../helpers/services/conversation/conversation.enums';
import { AskGeneratorHelpDetails, AskQuestionDetails } from '../../../../../../helpers/services/activity/activity.interface';
import { ActivityType } from '../../../../../../helpers/services/activity/activity.enums';

@Component({
  selector: 'app-generator-ai-helper',
  standalone: true,
  imports: [
    ChatConversationComponent
  ],
  templateUrl: './generator-ai-helper.component.html',
  styleUrl: './generator-ai-helper.component.scss'
})
export class GeneratorAiHelperComponent {
  readonly modelData = inject(MAT_DIALOG_DATA);
  conversationID: string | null = null;
  conversation: MessageI[] = [];
  messageUpdated = new EventEmitter<any>();
  thinking = false;


  constructor(
    private conversationService: ConversationService,
    private activityService: ActivityService
  ) {
    if (this.conversationID) {
      this.getConversation();
    }
  }

  startConversation(pendingMessage?: string) {
    this.conversationService.startConversations(pendingMessage || '', AssistantType.COURSE).subscribe((res) => {
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
      timestamp: Date.now().toString()
    };
    this.conversation.push(tempMessage);
    this.messageUpdated.emit();

    if (!this.conversationID) { this.startConversation(message); }
    else {
      // this.conversationService.askQuery(this.conversationID, message).subscribe((messages) => {
      //   this.conversation.pop();
      //   this.conversation = this.conversation.concat(messages);
      //   this.messageUpdated.emit();
      //   this.thinking = false;
      // })
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
    const currentSelection = this.modelData['currentSelection'];
    const timeLimit = this.modelData['timeLimit'];

    const details: AskGeneratorHelpDetails = {
      conversation_id: +this.conversationID,
      first_question: this.conversation[0].entities['user_query'],
      current_selection: currentSelection,
      time_limit: timeLimit
    }

    this.activityService.saveActivity({
      activity_type: ActivityType.GenerateHelpMessage,
      course: -1,
      details
    }).subscribe();
  }

}
