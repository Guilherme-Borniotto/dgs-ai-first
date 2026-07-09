import { z } from "zod";
import { logger } from "../shared/logger";

export const StructuredResponseSchema = z
  .object({
    answer: z.string().min(1, "answer is required"),
    source_document: z
      .array(z.string().min(1, "source document entry cannot be empty"))
      .min(1, "source_document must contain at least one source"),
    confidence_score: z.number().min(0).max(1),
  })
  .strict();

export type StructuredResponse = z.infer<typeof StructuredResponseSchema>;

const SAFE_FALLBACK_RESPONSE: StructuredResponse = {
  answer:
    "Nao foi possivel validar a resposta com seguranca. Encaminhe para analise humana da equipe de atendimento.",
  source_document: ["fallback-safe-response"],
  confidence_score: 0,
};

function normalizeText(value: string): string {
  return value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase();
}

function hasDangerousCargoTopic(text: string): boolean {
  return /(carga(s)?\s+perigosa(s)?|\bimo\b)/.test(text);
}

function hasReturnTopic(text: string): boolean {
  return /(devolucao|devolver|devolucoes)/.test(text);
}

function hasRequiredNegative(text: string): boolean {
  const negativePatterns = [
    /nao\s+(e\s+)?(possivel|permitida|permitido|elegivel)/,
    /nao\s+pode(m)?\s+(ser\s+)?devolv/,
    /nao\s+entra\s+no\s+processo\s+padrao/,
    /fora\s+do\s+processo\s+padrao/,
    /acionar\s+a\s+gestao\s+de\s+riscos/,
    /ramal\s+3800/,
  ];

  return negativePatterns.some((pattern) => pattern.test(text));
}

function hasForbiddenAffirmative(text: string): boolean {
  const affirmativePatterns = [
    /pode(m)?\s+(ser\s+)?devolv/,
    /devolucao\s+(e|esta)\s+(possivel|permitida)/,
    /(e|esta)\s+elegivel\s+para\s+devolucao/,
  ];

  return affirmativePatterns.some((pattern) => pattern.test(text));
}

function buildFallbackResponse(): StructuredResponse {
  return { ...SAFE_FALLBACK_RESPONSE };
}

export function validateAssistantResponse(rawResponse: unknown): StructuredResponse {
  if (
    typeof rawResponse !== "object" ||
    rawResponse === null ||
    !("source_document" in rawResponse)
  ) {
    logger.warn(
      { reason: "missing_source_document_field" },
      "Guardrail rejected response"
    );
    return buildFallbackResponse();
  }

  const parsed = StructuredResponseSchema.safeParse(rawResponse);

  if (!parsed.success) {
    logger.warn(
      {
        reason: "invalid_structured_output",
        issues: parsed.error.issues.map((issue) => ({
          path: issue.path.join("."),
          message: issue.message,
        })),
      },
      "Structured output validation failed"
    );
    return buildFallbackResponse();
  }

  const normalizedAnswer = normalizeText(parsed.data.answer);
  const referencesDangerousCargo = hasDangerousCargoTopic(normalizedAnswer);
  const referencesReturn = hasReturnTopic(normalizedAnswer);

  if (referencesDangerousCargo && referencesReturn) {
    if (hasForbiddenAffirmative(normalizedAnswer)) {
      logger.warn(
        { reason: "dangerous_cargo_return_affirmed" },
        "Guardrail blocked response"
      );
      return buildFallbackResponse();
    }

    if (!hasRequiredNegative(normalizedAnswer)) {
      logger.warn(
        { reason: "dangerous_cargo_return_missing_negative" },
        "Guardrail blocked response"
      );
      return buildFallbackResponse();
    }
  }

  return parsed.data;
}
