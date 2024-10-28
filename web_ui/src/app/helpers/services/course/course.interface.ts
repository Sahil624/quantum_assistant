export interface AvailableLOResponse {
    [key: string]: {
        [key: string]: {
          module_prereqs: string[]
          outcomes: {
            outcome: string
            outcome_mapping: string[]
          }[]
        }
    }
}

export type MyCourseResponse = CourseI[]

export interface CourseI {
  id: number
  title: string
  description: string
  created_at: string
  updated_at: string
  user: string
  learning_objects: LearningObject[]
}

export interface LearningObject {
  id: number
  object_id: string
  order: number
  started_on: string
  completed_on: string
  metadata: CellMetadata | null
}

export interface CellMetadata {
  cell_ID: string
  cell_alternates: string[]
  cell_concepts: string[]
  cell_estimated_time: string
  cell_interactive: string
  cell_outcomes: string[]
  cell_prereqs: string[]
  cell_title?: string
  cell_type: string[]
  module_outcomes: string[]
  module_prereqs: string[]
  module_title: string[]
}

export interface CellDataResponse {
  interactive: boolean
  content: string
  redirect_link: string
  quiz_cell: string
}

export interface UpdateLOStatusRequest {
  started_on?: string;
  completed_on?: string;
  id: number;
}

export interface CreateCourseRequest {
  title: string
  learning_object_ids: string[]
  description?: string;
}

export interface MetaDataI {
  [key:string]: {
    cell_estimated_time: string
    cell_prereqs: string[]
  }
}