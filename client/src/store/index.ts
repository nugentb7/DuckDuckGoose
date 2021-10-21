import { ThunkAction, ThunkDispatch } from 'redux-thunk';
import { combineReducers } from 'redux';
import { REQUEST_READINGS_ACTION_TYPE, RequestReadingsAction } from './reading';
import { readingsReducer } from './reading/reducers';

export type AppAction = RequestReadingsAction;

export type ActionType = REQUEST_READINGS_ACTION_TYPE;

/**
 * Alias for app-specific redux store dispatch function.
 */
export type AppDispatch = ThunkDispatch<RootState, unknown, AppAction>;
/**
 * Alias for app-specific thunk type.
 */
export type AppThunk = ThunkAction<void, RootState, unknown, AppAction>;

export enum AsyncActionStatus {
    Request = '@@REQUEST',
    Success = '@@SUCCESS',
    Failure = '@@FAILURE',
}

// The store needs to be passed a single reducer. We can create this by calling combineReducers
export const rootReducer = combineReducers({
    readings: readingsReducer,
});

/**
 * Root of state object, contains typing for the entire state tree.
 */
export type RootState = ReturnType<typeof rootReducer>;

/**
 * Initial value of state, as defined when the page loads BEFORE requests are made.
 */
export const InitialState: RootState = {
    readings: {},
};
