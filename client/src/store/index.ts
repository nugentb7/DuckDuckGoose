import { ThunkAction, ThunkDispatch } from "redux-thunk";
import { Action, combineReducers } from "redux";

export type AppAction = Action;

export type ActionType = null;

/**
 * Alias for app-specific redux store dispatch function.
 */
export type AppDispatch = ThunkDispatch<RootState, unknown, AppAction>;
/**
 * Alias for app-specific thunk type.
 */
export type AppThunk = ThunkAction<void, RootState, unknown, AppAction>;

export enum AsyncActionStatus {
  Request = "@@REQUEST",
  Success = "@@SUCCESS",
  Failure = "@@FAILURE",
}

// The store needs to be passed a single reducer. We can create this by calling combineReducers
export const rootReducer = combineReducers({});

/**
 * Root of state object, contains typing for the entire state tree.
 */
export type RootState = ReturnType<typeof rootReducer>;
