import { app, HttpRequest, HttpResponseInit, InvocationContext } from "@azure/functions";
import { CosmosClient } from "@azure/cosmos";
import { createHash, randomUUID } from "node:crypto";
import { ZodError } from "zod";
import { logger } from "../../shared/logger";
import { FeedbackRequest, validateFeedbackRequest } from "./validator";

type FeedbackDocument = {
  id: string;
  queryId: string;
  rating: number;
  comment?: string;
  attendantEmailHash?: string;
  timestamp: string;
};

const DATABASE_NAME = "novatech";
const CONTAINER_NAME = "feedbacks";

const cosmosConnectionString = process.env.COSMOS_CONNECTION_STRING;
const cosmosClient = cosmosConnectionString
  ? new CosmosClient(cosmosConnectionString)
  : undefined;
const cosmosContainer = cosmosClient
  ? cosmosClient.database(DATABASE_NAME).container(CONTAINER_NAME)
  : undefined;

function hashEmail(email: string): string {
  return createHash("sha256").update(email.trim().toLowerCase()).digest("hex");
}

function toDocument(payload: FeedbackRequest): FeedbackDocument {
  return {
    id: randomUUID(),
    queryId: payload.queryId,
    rating: payload.rating,
    comment: payload.comment,
    attendantEmailHash: payload.attendantEmail
      ? hashEmail(payload.attendantEmail)
      : undefined,
    timestamp: new Date().toISOString(),
  };
}

export async function feedbackHandler(
  request: HttpRequest,
  context: InvocationContext
): Promise<HttpResponseInit> {
  const log = logger.child({
    functionName: "feedback",
    invocationId: context.invocationId,
  });

  let body: unknown;

  try {
    body = await request.json();
  } catch {
    log.warn({ status: 400 }, "Feedback body is not valid JSON");
    return {
      status: 400,
      jsonBody: {
        error: "invalid_json",
        message: "Request body must be valid JSON",
      },
    };
  }

  let payload: FeedbackRequest;

  try {
    payload = validateFeedbackRequest(body);
  } catch (err) {
    if (err instanceof ZodError) {
      log.warn(
        {
          status: 400,
          issues: err.issues.map((issue) => ({
            field: issue.path.join("."),
            message: issue.message,
          })),
        },
        "Feedback input validation failed"
      );
      return {
        status: 400,
        jsonBody: {
          error: "validation_error",
          details: err.issues.map((issue) => ({
            field: issue.path.join("."),
            message: issue.message,
          })),
        },
      };
    }
    throw err;
  }

  if (!cosmosContainer) {
    log.error({ status: 500 }, "Cosmos DB is not configured");
    return {
      status: 500,
      jsonBody: {
        error: "internal_error",
        message: "Feedback storage is unavailable",
      },
    };
  }

  const document = toDocument(payload);

  try {
    await cosmosContainer.items.create(document);
  } catch (err) {
    log.error(
      {
        status: 500,
        err,
        queryId: payload.queryId,
      },
      "Failed to persist feedback"
    );

    return {
      status: 500,
      jsonBody: {
        error: "internal_error",
        message: "Could not persist feedback",
      },
    };
  }

  log.info(
    {
      status: 200,
      queryId: payload.queryId,
      rating: payload.rating,
      hasComment: Boolean(payload.comment),
      hasAttendantEmail: Boolean(payload.attendantEmail),
    },
    "Feedback persisted"
  );

  return {
    status: 200,
    jsonBody: {
      status: "ok",
    },
  };
}

app.http("feedback", {
  methods: ["POST"],
  authLevel: "function",
  route: "feedback",
  handler: feedbackHandler,
});
