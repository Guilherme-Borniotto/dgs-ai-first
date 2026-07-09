import pino from "pino";

export const logger = pino({
  name: "novatech-assistant",
  level: process.env.LOG_LEVEL ?? "info",
  base: undefined,
});
