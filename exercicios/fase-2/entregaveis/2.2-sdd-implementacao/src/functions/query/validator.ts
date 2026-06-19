import { z } from "zod";

// Input schema for POST /api/query
export const QueryRequestSchema = z.object({
  question: z
    .string()
    .min(1, "question cannot be empty")
    .max(1000, "question exceeds maximum length of 1000 characters")
    .trim(),
  sessionId: z
    .string()
    .uuid("sessionId must be a valid UUID")
    .optional(),
});

// Output schema — source_document is always present (product guardrail)
export const QueryResponseSchema = z.object({
  answer: z.string(),
  source_document: z.array(z.string()),
  confidence: z.enum(["high", "low"]),
  session_id: z.string().uuid().optional(),
});

export type QueryRequest = z.infer<typeof QueryRequestSchema>;
export type QueryResponse = z.infer<typeof QueryResponseSchema>;

export function validateRequest(body: unknown): QueryRequest {
  return QueryRequestSchema.parse(body);
}

export function validateResponse(response: unknown): QueryResponse {
  return QueryResponseSchema.parse(response);
}
