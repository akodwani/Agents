import { useEffect, useState } from 'react';

type AgentName = 'Job Machine' | 'Consultant' | 'Analyst';
type TabName = 'workspace' | 'logs' | 'files';

type StatusResponse = {
  backendOnline: boolean;
  budgetRemaining: string;
};

type RunResponse = {
  output: string;
};

type LogsResponse = {
  verify_events: string[];
  spending_log: string[];
};

type FilesResponse = {
  files: Array<{ name: string; size: number; modified: string }>;
};

const API_BASE = import.meta.env.VITE_BACKEND_URL ?? 'http://localhost:8000';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return (await response.json()) as T;
}

export function App() {
  const [selectedAgent, setSelectedAgent] = useState<AgentName>('Job Machine');
  const [selectedTab, setSelectedTab] = useState<TabName>('workspace');
  const [status, setStatus] = useState<StatusResponse>({ backendOnline: false, budgetRemaining: '--' });
  const [input, setInput] = useState('');
  const [output, setOutput] = useState('');
  const [logs, setLogs] = useState<LogsResponse>({ verify_events: [], spending_log: [] });
  const [files, setFiles] = useState<FilesResponse['files']>([]);
  const [running, setRunning] = useState(false);

  const refreshStatus = async () => {
    try {
      const result = await request<StatusResponse>('/status');
      setStatus(result);
    } catch {
      setStatus((current) => ({ ...current, backendOnline: false }));
    }
  };

  const refreshLogs = async () => {
    const result = await request<LogsResponse>('/logs?limit=200');
    setLogs(result);
  };

  const refreshFiles = async () => {
    const result = await request<FilesResponse>('/files');
    setFiles(result.files);
  };

  useEffect(() => {
    void refreshStatus();
    const interval = window.setInterval(() => {
      void refreshStatus();
    }, 5000);

    return () => window.clearInterval(interval);
  }, []);

  useEffect(() => {
    if (selectedTab === 'logs') {
      void refreshLogs();
    }
    if (selectedTab === 'files') {
      void refreshFiles();
    }
  }, [selectedTab]);

  const runAgent = async () => {
    setRunning(true);
    try {
      const result = await request<RunResponse>('/run', {
        method: 'POST',
        body: JSON.stringify({
          agent: selectedAgent,
          input,
        }),
      });
      setOutput(result.output);
    } catch (error) {
      setOutput(`Run failed: ${(error as Error).message}`);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="app-shell">
      <header className="top-bar">
        <strong>Agent Workspace</strong>
        <div className="status-row">
          <span>Backend: {status.backendOnline ? 'online' : 'offline'}</span>
          <span>Budget remaining: {status.budgetRemaining}</span>
        </div>
      </header>

      <div className="body">
        <aside className="sidebar">
          <h3>Agents</h3>
          {(['Job Machine', 'Consultant', 'Analyst'] as AgentName[]).map((agent) => (
            <button
              key={agent}
              className={selectedAgent === agent ? 'active' : ''}
              onClick={() => setSelectedAgent(agent)}
            >
              {agent}
            </button>
          ))}

          <hr />
          <button className={selectedTab === 'workspace' ? 'active' : ''} onClick={() => setSelectedTab('workspace')}>
            Workspace
          </button>
          <button className={selectedTab === 'logs' ? 'active' : ''} onClick={() => setSelectedTab('logs')}>
            Logs
          </button>
          <button className={selectedTab === 'files' ? 'active' : ''} onClick={() => setSelectedTab('files')}>
            Files
          </button>
        </aside>

        <main className="main-panel">
          {selectedTab === 'workspace' && (
            <>
              <label htmlFor="agent-input">Input</label>
              <textarea id="agent-input" value={input} onChange={(event) => setInput(event.target.value)} rows={8} />
              <button onClick={() => void runAgent()} disabled={running || input.trim().length === 0}>
                {running ? 'Running...' : 'Run'}
              </button>
              <label htmlFor="agent-output">Output</label>
              <pre id="agent-output" className="output-pane">
                {output || 'No output yet.'}
              </pre>
            </>
          )}

          {selectedTab === 'logs' && (
            <div className="logs-grid">
              <section>
                <h3>verify_events (last 200 lines)</h3>
                <pre>{logs.verify_events.join('\n') || 'No log data.'}</pre>
              </section>
              <section>
                <h3>spending_log (last 200 lines)</h3>
                <pre>{logs.spending_log.join('\n') || 'No log data.'}</pre>
              </section>
            </div>
          )}

          {selectedTab === 'files' && (
            <section>
              <h3>Generated outputs (./outputs)</h3>
              <button onClick={() => void window.electronAPI?.openOutputsFolder()}>Open folder</button>
              <ul>
                {files.map((file) => (
                  <li key={file.name}>
                    {file.name} - {file.size} bytes - {new Date(file.modified).toLocaleString()}
                  </li>
                ))}
              </ul>
              {files.length === 0 && <p>No files listed.</p>}
            </section>
          )}
        </main>
      </div>
    </div>
  );
}
