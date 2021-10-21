import { REQUEST_READINGS_SUCCESS, RequestReadingsAction } from './index';

const InitialReadingsState = {};
export function readingsReducer(state: any = InitialReadingsState, action: RequestReadingsAction) {
    switch (action.type) {
        case 'REQUEST_READINGS_STARTED':
            return {
                ...state,
                isFetching: true,
            };
        case REQUEST_READINGS_SUCCESS:
            if (action.response.entities.readings) {
                return {
                    ...state,
                    readings: {},
                    isFetching: false,
                };
            } else {
                return {
                    ...state,
                    isFetching: false,
                };
            }
        case 'REQUEST_READINGS_FAILURE':
            return {
                ...state,
                isFetching: false,
            };
        default:
            return state;
    }
}
