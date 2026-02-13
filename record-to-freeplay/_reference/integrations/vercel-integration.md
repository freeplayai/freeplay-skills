# Vercel AI SDK + Freeplay Integration Reference

Reference examples illustrating integration patterns with Vercel AI SDK. These show the general approach - your implementation will differ based on your application structure.

## Installation

```bash
npm install @freeplayai/vercel @vercel/otel @arizeai/openinference-vercel @opentelemetry/api
```

For Node.js applications (non-Next.js), also install:
```bash
npm install @opentelemetry/sdk-trace-base
```

## Environment Setup

```bash
FREEPLAY_API_KEY=your_freeplay_api_key
FREEPLAY_PROJECT_ID=your_project_id

# For custom domains (optional):
# FREEPLAY_OTEL_ENDPOINT=https://acme.freeplay.ai/api/v0/otel/v1/traces
```

## OpenTelemetry Setup (Next.js)

Reference example showing `instrumentation.ts` pattern:

```typescript
import { registerOTel } from "@vercel/otel";
import { createFreeplaySpanProcessor } from "@freeplayai/vercel";

export function register() {
  registerOTel({
    serviceName: "my-nextjs-app",
    spanProcessors: [createFreeplaySpanProcessor()],
  });
}
```

## Reference Example

Example showing API route pattern with Freeplay prompts:

```typescript
import { streamText } from "ai";
import {
  getPrompt,
  FreeplayModel,
  createFreeplayTelemetry
} from "@freeplayai/vercel";

export async function POST(req: Request) {
  const { messages, chatId } = await req.json();

  const inputVariables = {
    customer_issue: "I can't log into my account",
  };

  // Fetch prompt from Freeplay
  const prompt = await getPrompt({
    templateName: "customer-support-agent",
    variables: inputVariables,
    messages,  // Pass conversation history
  });

  // Get model configured in Freeplay
  const model = await FreeplayModel(prompt);

  // Stream with automatic telemetry
  const result = streamText({
    model,
    messages,
    system: prompt.systemContent,
    experimental_telemetry: createFreeplayTelemetry(prompt, {
      functionId: "customer-support-chat",
      sessionId: chatId,
      inputVariables,
    }),
  });

  return result.toDataStreamResponse();
}
```

## Key Concepts

**Automatic Instrumentation:**
- OpenTelemetry setup captures traces automatically
- No manual logging calls needed
- Traces sent to Freeplay via OTEL protocol

**Prompt Management:**
- `getPrompt()` fetches prompts from Freeplay
- Pass conversation `messages` for history
- `prompt.systemContent` contains system message

**Model and model parameters are managed in Freeplay:**
- `FreeplayModel()` fetches the model, provider, and parameters (temperature, max_tokens, etc.) from the Freeplay prompt template
- Generated code should never hardcode model names or parameters

**Telemetry Context:**
- `functionId`: Identifies the operation (e.g., "chat", "summarize")
- `sessionId`: Groups related interactions
- `inputVariables`: Logged for debugging/filtering

## What Gets Logged

- Complete conversation messages
- Prompt template used
- Input variables
- Model and provider
- Latency and token usage
- Session grouping
- Function/operation name

## Notes

These reference examples illustrate the general pattern. Your actual implementation will differ based on your:
- Next.js app structure and routing
- Error handling approach
- Session management strategy
- Metadata and filtering needs
- Model configurations

## Resources

- [Vercel AI SDK Docs](https://sdk.vercel.ai/docs)
- [Freeplay Vercel Integration Docs](https://docs.freeplay.ai/docs/vercel)
