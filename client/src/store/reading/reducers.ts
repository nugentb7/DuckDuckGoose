import { Reading, REQUEST_READINGS_SUCCESS, RequestReadingsAction } from './index';
import { act } from 'react-dom/test-utils';

interface ReadingsState {
    entities: Map<number, Reading>;
}

const InitialReadingsState = {};
export function readingsReducer(state: any = InitialReadingsState, action: RequestReadingsAction): ReadingsState {
    switch (action.type) {
        case 'REQUEST_READINGS_STARTED':
            return {
                ...state,
                isFetching: true,
            };
        case REQUEST_READINGS_SUCCESS:
            if (action.response.entities.reading) {
                for (const reading of Object.values(action.response.entities.reading)) {
                    reading.date = new Date(reading.date);
                }

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
