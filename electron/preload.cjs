const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  openOutputsFolder: () => ipcRenderer.invoke('open-outputs-folder'),
});
