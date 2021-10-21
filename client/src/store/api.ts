import { Middleware } from "redux";
import { AppAction, AsyncActionStatus, RootState } from "./index";
import { normalize, schema } from "normalizr";

export const API_ROOT = "http://localhost:5000/api/v1/";
export const CALL_API = "CALL_API";

export interface ApiRequest {
  [CALL_API]: {
    endpoint: string | Function;
    schema: schema.Entity | schema.Entity[];
    method: "GET" | "PUT" | "POST" | "DELETE";
    body: Record<string, string | number>;
    types: {
      [AsyncActionStatus.Request]: string;
      [AsyncActionStatus.Success]: string;
      [AsyncActionStatus.Failure]: string;
    };
  };
}

// Fetches an API response and normalizes the result JSON according to schema.
// This makes every API response have the same shape, regardless of how nested it was.
// TODO I should change the type of 'method' to an actual type and not just string
const callApi = async (
  endpoint: string,
  schema: schema.Entity | schema.Entity[],
  method: string,
  body?: Record<string, string | number>
) => {
  const fullUrl =
    endpoint.indexOf(API_ROOT) === -1 ? API_ROOT + endpoint : endpoint;

  let formData = new FormData();
  if (body) {
    for (const key of Object.keys(body)) {
      formData.append(key, body[key].toString());
    }
  }

  // console.warn('Form data');
  // console.warn(formData);

  let fetchParam: RequestInit = {
    method: method,
    body: ["POST", "PUT"].includes(method) ? formData : null,
    credentials: "include",
  };

  // console.warn(`Sending request to ${fullUrl}`);
  // console.warn(fetchParam);

  const response = await fetch(fullUrl, fetchParam);
  const json = await response.json();
  // console.warn(`Call to ${fullUrl}: OK!`);
  // console.warn(json);

  if (!response.ok) {
    throw new Error(json);
  }

  // We use Normalizr to transform API responses from a nested form
  // to a flat form where individual objects are placed in `entities`, and nested
  // JSON objects are replaced with their IDs. This is very convenient for
  // consumption by reducers, because we can easily build a normalized tree
  // and keep it updated as we fetch more data.

  // Read more about Normalizr: https://github.com/paularmstrong/normalizr
  return normalize(json, schema);
};

export const apiMiddleware: Middleware<{}, RootState> = (store) => (next) => (
  action: AppAction
) => {
  if ((action as any).hasOwnProperty(CALL_API)) {
    const apiRequest = (action as unknown) as ApiRequest;
    const callAPI = apiRequest[CALL_API];
    if (typeof callAPI === "undefined") {
      return next(action);
    }

    let { endpoint } = callAPI;
    const { schema, types, body, method } = callAPI;

    if (typeof endpoint === "function") {
      endpoint = endpoint(store.getState());
    }

    if (typeof endpoint !== "string") {
      throw new Error("Specify a string endpoint URL.");
    }
    if (!schema) {
      throw new Error("Specify one of the exported Schemas.");
    }

    const actionWith = (data: any) => {
      const finalAction = Object.assign({}, action, data);
      delete finalAction[CALL_API];
      return finalAction;
    };

    const requestType = types[AsyncActionStatus.Request];
    const successType = types[AsyncActionStatus.Success];
    const failureType = types[AsyncActionStatus.Failure];

    next(actionWith({ type: requestType }));
    return callApi(endpoint, schema, method, body).then(
      (response) =>
        next(
          actionWith({
            response,
            type: successType,
          })
        ),
      (error) =>
        next(
          actionWith({
            type: failureType,
            error: error.message || "Something bad happened",
          })
        )
    );
  } else {
    return next(action);
  }
};
