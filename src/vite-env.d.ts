/// <reference types="vite/client" />

interface Window {
  electronAPI?: {
    openOutputsFolder: () => Promise<void>;
  };
}
