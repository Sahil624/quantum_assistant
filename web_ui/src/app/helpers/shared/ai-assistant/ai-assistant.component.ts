import { Component } from '@angular/core';
import { ChatConversationComponent } from '../chat-conversation/chat-conversation.component';
import { StudyAssistantSocketService } from '../../services/websockets/study-assistant-socket/study-assistant-socket.service';
import { ConversationMessageI } from '../../services/websockets/study-assistant-socket/study-assistant.interface';

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
  conversationID: string | null = null;

  constructor(
    public studyAssistantService: StudyAssistantSocketService
  ) {
  }

  startConversation(pendingMessage?: string) {
    this.studyAssistantService.startConversation(this.conversationID).then((conversationID) => {
      this.conversationID = conversationID;

      if (pendingMessage) {
        this.studyAssistantService.sendMessage(this.conversationID, pendingMessage);
      }
    })
  }

  sendMessage(message: string) {
    if (!this.conversationID) {
      this.startConversation(message);
      return;
    }
    this.studyAssistantService.sendMessage(this.conversationID, { message });
  }

  getConversation(): ConversationMessageI[] {
    if (!this.conversationID) { return [] }
    const conversation = this.studyAssistantService.conversationMap.get(this.conversationID);
    if (!conversation) { return [] }
    return conversation
  }
}
