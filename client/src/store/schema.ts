import { schema } from 'normalizr';

const readingSchema = new schema.Entity(
    'reading',
    {},
    {
        idAttribute: (value) => value.id,
    }
);

export const SCHEMAS = {
    READING: readingSchema,
    READING_ARRAY: [readingSchema],
};
