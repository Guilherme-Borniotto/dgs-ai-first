import { app, HttpRequest, HttpResponseInit, InvocationContext } from "@azure/functions";
import { ZodError } from "zod";
import { validateRequest, validateResponse, QueryResponse } from "./validator";
import { logger } from "../../shared/logger";

// TASK-001: HTTP trigger setup with input validation only.
// Services (embedding, search, completion) are wired in TASK-007.
export async function queryHandler(
  request: HttpRequest,
  context: InvocationContext
): Promise<HttpResponseInit> {
  const start = Date.now();
  const log = logger.child({ functionName: "query", invocationId: context.invocationId });

  let body: unknown;

  try {
    body = await request.json();
  } catch {
    log.warn({ status: 400 }, "Failed to parse request body as JSON");
    return {
      status: 400,
      jsonBody: { error: "invalid_json", message: "Request body must be valid JSON" },
    };
  }

  let question: string;
  let sessionId: string | undefined;

  try {
    const validated = validateRequest(body);
    question = validated.question;
    sessionId = validated.sessionId;
  } catch (err) {
    if (err instanceof ZodError) {
      log.warn({ status: 400, issues: err.issues }, "Input validation failed");
      return {
        status: 400,
        jsonBody: {
          error: "validation_error",
          details: err.issues.map((i) => ({ field: i.path.join("."), message: i.message })),
        },
      };
    }
    throw err;
  }

  log.info({ sessionId, questionLength: question.length }, "Query request received");

  // Stub response for TASK-001 — real pipeline wired in TASK-007
  const stubResponse: QueryResponse = {
    answer: "[STUB] Pipeline not yet implemented — see TASK-007",
    source_document: [],
    confidence: "low",
    ...(sessionId && { session_id: sessionId }),
  };

  const validated = validateResponse(stubResponse);
  const latencyMs = Date.now() - start;

  log.info({ status: 200, latencyMs, sessionId }, "Query response sent");

  return {
    status: 200,
    jsonBody: validated,
  };
}

app.http("query", {
  methods: ["POST"],
  authLevel: "function",
  route: "query",
  handler: queryHandler,
});
