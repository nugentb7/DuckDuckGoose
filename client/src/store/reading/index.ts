import { ApiRequest } from '../api';

/**
 * A valid string representing a location.
 */
export type Location =
    | 'Boonsri'
    | 'Kannika'
    | 'Chai'
    | 'Kohsoom'
    | 'Somchair'
    | 'Sakda'
    | 'Busarakhan'
    | 'Tansanee'
    | 'Achara'
    | 'Decha';

/**
 * A valid string representing a type of unit.
 */
export type Unit = 'mg/l' | 'µg/l' | 'C' | '';

/**
 * A single reading (e.g. row) with all associated data.
 */
export interface Reading {
    id: number;
    value: number;
    location: Location;
    measure: string;
    date: Date;
    unit: Unit;
}

export const REQUEST_READINGS_STARTED = 'REQUEST_READINGS_STARTED';
export const REQUEST_READINGS_SUCCESS = 'REQUEST_READINGS_SUCCESS';
export const REQUEST_READINGS_FAILURE = 'REQUEST_READINGS_FAILURE';

export type REQUEST_READINGS_STARTED = typeof REQUEST_READINGS_STARTED;
export type REQUEST_READINGS_SUCCESS = typeof REQUEST_READINGS_SUCCESS;
export type REQUEST_READINGS_FAILURE = typeof REQUEST_READINGS_FAILURE;

export type REQUEST_READINGS_ACTION_TYPE =
    | REQUEST_READINGS_STARTED
    | REQUEST_READINGS_SUCCESS
    | REQUEST_READINGS_FAILURE;

export interface RequestReadingsStarted extends ApiRequest {
    type: REQUEST_READINGS_STARTED;
    // TODO: args for the request will go here (e.g. page number or number of entries)
}

export interface RequestReadingsSuccess {
    type: REQUEST_READINGS_SUCCESS;
    response: {
        entities: {
            reading?: Record<number, Reading>;
        };
    };
}

export interface RequestReadingsFailure {
    type: REQUEST_READINGS_FAILURE;
}

export type RequestReadingsAction = RequestReadingsStarted | RequestReadingsSuccess | RequestReadingsFailure;
