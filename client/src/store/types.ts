export interface Paginated<T> {
    /**
     * Set of all acquired ids.
     */
    ids: number[];
    /**
     * Mapping of ids to their corresponding entities.
     */
    entities: Record<number, T>;
    /**
     * If a request is pending or not.
     */
    isFetching: boolean;
}

export interface NestedPaginated<T> {
    /**
     * Set of all acquired ids.
     */
    ids: number[];
    /**
     * Mapping of ids to their corresponding entities.
     */
    entities: Record<number, Record<number, T>>;
    /**
     * If a request is pending or not.
     */
    isFetching: boolean;
}
