import { REQUEST_READINGS_SUCCESS, RequestReadingsAction } from './index';
import { RootState } from '../index';

const InitialReadingsState = {};
export function readingsReducer(state: any = InitialReadingsState, action: RequestReadingsAction) {
    switch (action.type) {
        case 'REQUEST_READINGS_STARTED':
            return {
                ...state,
                isFetching: true,
            };
        case REQUEST_READINGS_SUCCESS:
            if (action.response.entities.reading) {
                return {
                    ...state,
                    entities: {
                        ...state?.readings?.entities,
                        ...action.response.entities.reading,
                    },
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
