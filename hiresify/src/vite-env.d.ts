/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_HOST: string;
  readonly VITE_API_PORT: string;
  readonly VITE_API_SCHEME: string;

  readonly VITE_APP_HOST: string;
  readonly VITE_APP_PORT: string;
  readonly VITE_APP_SCHEME: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
