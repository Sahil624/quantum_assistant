import { ActivityType } from "./activity.enums"

interface ActivityDetails {};

export interface ViewContentDetails extends ActivityDetails {
    viewed_cell: string
    movement?: 'next' | 'previous' | 'skip'
}

export interface AskQuestionDetails extends ActivityDetails {
    conversation_id: number
    first_question: string
    lo_opened: string
}

export interface AskGeneratorHelpDetails extends ActivityDetails {
    conversation_id: number
    first_question: string
    current_selection: string[]
    time_limit: number
}


export interface RecordActivityRequest {
    course: number
    activity_type: ActivityType
    details: ActivityDetails
}