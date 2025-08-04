/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_ORIGIN: string;
  readonly VITE_CHUNK_SIZE: string;
  readonly VITE_MAX_JOBNUM: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
