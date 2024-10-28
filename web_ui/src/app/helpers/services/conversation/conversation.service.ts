import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { assistantQueryUrl, conversationsUrl } from '../../urls';
import { ConversationBrief, ConversationI, CreateConversationResponse, MessageI } from './conversation.interface';
import { AssistantType } from './conversation.enums';

@Injectable({
  providedIn: 'root'
})
export class ConversationService {

  constructor(
    private http: HttpClient
  ) { }

  getConversations() {
    return this.http.get<ConversationBrief>(conversationsUrl);
  }

  getConversation(id: string) {
    return this.http.get<ConversationI>(conversationsUrl + id + '/');
  }

  startConversations(title: string, assistantType: AssistantType) {
    return this.http.post<CreateConversationResponse>(conversationsUrl, { title, assistant_type: assistantType });
  }

  askQuery(conversationID: string, query: string, enableExternalSource: boolean) {
    const params = { query } as any;

    if(enableExternalSource) {
      params['include_external_data'] = enableExternalSource
    }

    return this.http.post<MessageI[]>(assistantQueryUrl + conversationID + '/', params)
  }


  askGenerateHelpQuery(conversationID: number, query: string) {
    
  }

}
