import { MessageType } from "./conversation.enums"

export interface ConversationBrief {
    id: number
    title: string
    created_at: string
    updated_at: string
}

export interface CreateConversationResponse {
    id: number
    title: string
    created_at: string
    updated_at: string
    system_prompt_type: string
}


export interface MessageI {
    id: number
    content: string
    message_type: MessageType
    timestamp: string
    is_answer: boolean
    is_original_user_query: boolean
    is_out_of_context_message?: boolean
    entities: {
        [key: string]: string
    }
}

export interface ConversationI extends ConversationBrief {
    messages: MessageI[]
}

