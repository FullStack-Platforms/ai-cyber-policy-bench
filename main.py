from langchain_community.callbacks.confident_callback import DeepEvalCallbackHandler
from langchain_openai import OpenAI

llms = [
    "anthropic/claude-3.7-sonnet",
    "anthropic/claude-opus-4",
    "anthropic/claude-opus-4.1",
    "anthropic/claude-sonnet-4",
    "deepseek/deepseek-r1-0528",
    "google/gemini-2.5-flash",
    "google/gemini-2.5-pro",
    "moonshotai/kimi-k2",
    "openai/gpt-5-chat",
    "openai/gpt-5-mini",
    "openai/gpt-5-nano",
    "qwen/qwen3-235b-a22b-2507"
]

const chat = new ChatOpenAI(
  {
    model: '<model_name>',
    temperature: 0.8,
    streaming: true,
    apiKey: '${API_KEY_REF}',
  },
  {
    baseURL: 'https://openrouter.ai/api/v1',
    defaultHeaders: {
      'HTTP-Referer': '<YOUR_SITE_URL>', // Optional. Site URL for rankings on openrouter.ai.
      'X-Title': '<YOUR_SITE_NAME>', // Optional. Site title for rankings on openrouter.ai.
    },
  },
);

// Example usage
const response = await chat.invoke([
  new SystemMessage("You are a helpful assistant."),
  new HumanMessage("Hello, how are you?"),
]);
