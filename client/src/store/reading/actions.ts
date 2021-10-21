import {
  REQUEST_READINGS_FAILURE,
  REQUEST_READINGS_STARTED,
  REQUEST_READINGS_SUCCESS,
  RequestReadingsStarted,
} from "./index";
import { CALL_API } from "../api";
import { SCHEMAS } from "../schema";
import { AsyncActionStatus } from "../index";

export function requestReadings(): RequestReadingsStarted {
  return {
    type: REQUEST_READINGS_STARTED,
    [CALL_API]: {
      body: {}, // body arguments can be added to the request here
      endpoint: `data`, // if you have arguments you can map them here
      method: "GET",
      schema: SCHEMAS["READING"],
      types: {
        [AsyncActionStatus.Request]: REQUEST_READINGS_STARTED,
        [AsyncActionStatus.Success]: REQUEST_READINGS_SUCCESS,
        [AsyncActionStatus.Failure]: REQUEST_READINGS_FAILURE,
      },
    },
  };
}
