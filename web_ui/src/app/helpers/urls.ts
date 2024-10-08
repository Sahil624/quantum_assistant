import { environment } from "../../environments/environment";


const host = environment.host;

export const studyAssistantSocketUrl = `${host}/ws/assistant/`;

export const loginUrl = `${host}/api/v1/users/login/`;
export const refreshUrl = `${host}/api/v1/users/refresh/`;
export const availableLOUrl = `${host}/api/v1/course/available_lo/`;
export const cellDataUrl = `${host}/api/v1/course/cell/`;
export const updateLOStatusUrl = `${host}/api/v1/course/update_learning_objects/`;
export const myCoursesUrl = `${host}/api/v1/course/courses/`;