export const PROVIDERS = [
  { id: "mock",       label: "Mock (Offline)",     defaultModel: "mock",                         contextLimit: 9999 },
  { id: "openai",     label: "OpenAI",              defaultModel: "text-embedding-3-small",       contextLimit: 8191 },
  { id: "gemini",     label: "Google Gemini",       defaultModel: "text-embedding-004",           contextLimit: 2048 },
  { id: "anthropic",  label: "Anthropic",           defaultModel: "claude-3-haiku-20240307",      contextLimit: 200000 },
  { id: "openrouter", label: "OpenRouter",          defaultModel: "openai/text-embedding-3-small", contextLimit: 8191 },
  { id: "ollama",     label: "Ollama (Local)",      defaultModel: "llama3.1",                     contextLimit: 4096 },
  { id: "lmstudio",   label: "LM Studio (Local)",   defaultModel: "nomic-embed-text",             contextLimit: 8192 },
];

export const DEFAULT_PROVIDER = PROVIDERS[0];
