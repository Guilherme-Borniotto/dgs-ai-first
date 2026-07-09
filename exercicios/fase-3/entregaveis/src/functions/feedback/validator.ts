import { z } from "zod";

export const FeedbackRequestSchema = z
  .object({
    queryId: z.string().trim().min(1, "queryId is required").max(120),
    rating: z.coerce.number().int().min(1).max(5),
    comment: z.string().trim().max(1000).optional(),
    attendantEmail: z.string().trim().email().optional(),
  })
  .strict();

export type FeedbackRequest = z.infer<typeof FeedbackRequestSchema>;

export function validateFeedbackRequest(body: unknown): FeedbackRequest {
  return FeedbackRequestSchema.parse(body);
}
