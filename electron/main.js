const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const axios = require('axios');

let mainWindow;
let backendProcess;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    },
    title: "ChunkLab Native",
    backgroundColor: '#0f172a' // match slate-900
  });

  // In production, load the index.html from the build folder
  // In development, load from the dev server
  const isDev = !app.isPackaged;
  if (isDev) {
    mainWindow.loadURL('http://localhost:5173');
    // mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '../frontend/dist/index.html'));
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

function startBackend() {
  const isDev = !app.isPackaged;
  let backendPath;
  let cwd;

  if (isDev) {
    backendPath = 'python';
    cwd = path.join(__dirname, '..');
    const args = ['-m', 'backend.main'];
    backendProcess = spawn(backendPath, args, { cwd, shell: true });
  } else {
    // Di Windows, backend.exe diletakkan di folder 'Resources' oleh electron-builder
    backendPath = path.join(process.resourcesPath, 'backend.exe');
    cwd = process.resourcesPath;
    backendProcess = spawn(backendPath, [], { cwd, shell: true });
  }

  backendProcess.stdout.on('data', (data) => {
    console.log(`Backend: ${data}`);
  });

  backendProcess.stderr.on('data', (data) => {
    console.error(`Backend Error: ${data}`);
  });
  
  backendProcess.on('error', (err) => {
    console.error('Failed to start backend process:', err);
  });
}

app.on('ready', () => {
  startBackend();
  createWindow();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('quit', () => {
  if (backendProcess) {
    // Kill the backend process when electron quits
    if (process.platform === 'win32') {
        spawn("taskkill", ["/pid", backendProcess.pid, '/f', '/t']);
    } else {
        backendProcess.kill();
    }
  }
});
