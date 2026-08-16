export const PROVIDER_NAMES = {
  umumiy: "AI asoslari",
  chatgpt: "ChatGPT",
  gemini: "Google Gemini",
  claude: "Claude",
  cursor: "Cursor",
  xai: "xAI (Grok)",
  meta: "Meta AI",
  deepseek: "DeepSeek",
  qwen: "Qwen",
  microsoft: "Microsoft AI",
  robototexnika: "Robototexnika",
};

export const DIFFICULTY_NAMES = {
  boshlangich: "Boshlang'ich",
  orta: "O'rta",
  ilgor: "Ilg'or",
};

export function providerName(value) {
  return PROVIDER_NAMES[value] || value;
}

export function difficultyName(value) {
  return DIFFICULTY_NAMES[value] || value;
}
