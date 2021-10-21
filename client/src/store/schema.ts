import { schema } from "normalizr";

const readingSchema = new schema.Entity("reading", {});

export const SCHEMAS = {
  READING: readingSchema,
};
