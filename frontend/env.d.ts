/// <reference types="vite/client" />

// As variáveis de ambiente que o frontend conhece — tipadas · the env vars the frontend knows, typed
interface ImportMetaEnv {
  readonly VITE_API_URL?: string
}
interface ImportMeta {
  readonly env: ImportMetaEnv
}
