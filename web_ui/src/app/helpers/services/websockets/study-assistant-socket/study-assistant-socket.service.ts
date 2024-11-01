import { Injectable } from '@angular/core';
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';
import { studyAssistantSocketUrl } from '../../../urls';
import { getAccessToken } from '../../../storage';
import { ConversationMessageI } from './study-assistant.interface';


@Injectable({
  providedIn: 'root'
})
export class StudyAssistantSocketService {
  conversationMap = new Map<string, ConversationMessageI[]>();
  conversationSocketMap = new Map<string, WebSocketSubject<any>>();

  constructor() { }

  startConversation(conversationID?: string | null) {
    return new Promise<string>((resolve) => {
      if(conversationID && this.conversationSocketMap.has(conversationID)) {
        resolve(conversationID);
        return;
      }

      let url = studyAssistantSocketUrl;

      if (conversationID) {
        url += conversationID + '/'
      }

      url = url + '?' + getAccessToken();
      const subject = webSocket(url);

      const messageFunc = (msg: any) => {
        if (!conversationID) {
          if (msg['type'] == 'conversation_acknowledge') {
            const conversationID = msg['message']

            this.conversationSocketMap.set(conversationID, subject);
            this.conversationMap.set(conversationID, [])

            resolve(conversationID);
          }
        }
        if (conversationID) {
          this.onMessage(conversationID, msg);
        }
      }

      subject.subscribe({
        next: messageFunc.bind(this),
        error: this.onError.bind(this),
        complete: this.onDisconnect.bind(this)
      })
    })
  }

  onAssistantMessage(conversationId: string,msg: any) {
    const message = msg.message.concept_explanation;
    const conversation = this.conversationMap.get(conversationId);

    if(!conversation) {
      console.error(`Message received for unknown conversation ${conversation}`, msg);
      return;
    }

    conversation.push({
      from: 'system',
      message
    })
  }

  onMessage(conversationId: string, msg: any) {
    switch (msg['type']) {
      case 'assistant_message':
        this.onAssistantMessage(conversationId, msg);
        break;
    
      default:
        console.error(`Unknown Message received`, msg)
        break;
    }
  }

  onError(err: any) {
    console.log("ERR", err)
  }

  onDisconnect() {
    console.log('Disconnect')
  }

  sendMessage(conversationID: string, msg: any) {
    const subject = this.conversationSocketMap.get(conversationID);
    if(!subject) {
      console.error(`Tried to send message on unknown conversation. ${conversationID}`, msg);
      return;
    }

    const conversation = this.conversationMap.get(conversationID);
    if(!conversation) {
      console.error(`Tried to send message on unknown conversation. ${conversationID}`, msg);
      return;
    }

    subject.next(msg);
    conversation.push({
      from: 'user',
      message: msg['message']
    })
  }
}
