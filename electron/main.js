/**
 * electron/main.js — PranshulOS desktop shell
 *
 * Responsibilities:
 * 1. Spawn the Flask backend (python main.py or the bundled exe)
 * 2. Poll localhost:5000/api/ping until Flask is ready
 * 3. Open a frameless Chromium window pointing at localhost:5000/home
 * 4. Kill Flask when the window closes
 */

const { app, BrowserWindow, shell } = require('electron');
const { spawn }                      = require('child_process');
const path                           = require('path');
const http                           = require('http');

let mainWindow  = null;
let flaskProcess = null;

// ── Start Flask ───────────────────────────────────────────────────────────────

function startFlask() {
  const isDev = !app.isPackaged;

  let cmd, args, cwd;

  if (isDev) {
    // Dev mode: run python main.py from repo root
    cmd  = process.platform === 'win32' ? 'python' : 'python3';
    args = ['main.py'];
    cwd  = path.join(__dirname, '..');   // repo root (one level above electron/)
  } else {
    // Packaged mode: run the bundled flask.exe next to the Electron exe
    cmd  = path.join(process.resourcesPath, 'flask', 'flask.exe');
    args = [];
    cwd  = path.join(process.resourcesPath, 'flask');
  }

  flaskProcess = spawn(cmd, args, {
    cwd,
    stdio: 'ignore',   // suppress Flask console output in packaged mode
    windowsHide: true, // don't show a console window on Windows
  });

  flaskProcess.on('error', (err) => {
    console.error('Flask failed to start:', err);
  });
}

// ── Poll until Flask is ready ─────────────────────────────────────────────────

function waitForFlask(retries = 30, interval = 300) {
  return new Promise((resolve, reject) => {
    let attempts = 0;

    const check = () => {
      const req = http.get('http://127.0.0.1:5000/api/ping', (res) => {
        if (res.statusCode === 200) {
          resolve();
        } else {
          retry();
        }
      });
      req.on('error', retry);
      req.setTimeout(500, () => { req.destroy(); retry(); });
    };

    const retry = () => {
      attempts++;
      if (attempts >= retries) {
        reject(new Error('Flask did not start in time'));
      } else {
        setTimeout(check, interval);
      }
    };

    check();
  });
}

// ── Create window ─────────────────────────────────────────────────────────────

function createWindow() {
  mainWindow = new BrowserWindow({
    width:           1100,
    height:          720,
    minWidth:        860,
    minHeight:       560,
    backgroundColor: '#0c0c0c',
    webPreferences: {
      preload:          path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration:  false,
    },
    // Keep the native title bar for now — can make frameless later
    autoHideMenuBar: true,
  });

  mainWindow.loadURL('http://127.0.0.1:5000/');

  // Open external links (from fetch('/launch/...') webbrowser.open calls)
  // in the system default browser, not in the Electron window
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// ── App lifecycle ─────────────────────────────────────────────────────────────

app.whenReady().then(async () => {
  startFlask();

  try {
    await waitForFlask();
    createWindow();
  } catch (err) {
    console.error('Could not connect to Flask:', err.message);
    app.quit();
  }
});

app.on('window-all-closed', () => {
  // Kill Flask when all windows are closed
  if (flaskProcess) {
    flaskProcess.kill();
    flaskProcess = null;
  }
  app.quit();
});

app.on('activate', async () => {
  // macOS: re-open window if dock icon clicked with no windows open
  if (BrowserWindow.getAllWindows().length === 0) {
    try {
      await waitForFlask(10, 200);
      createWindow();
    } catch (_) {}
  }
});
