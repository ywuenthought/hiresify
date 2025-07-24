/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_ORIGIN: string;
  readonly VITE_CHUNK_SIZE: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
