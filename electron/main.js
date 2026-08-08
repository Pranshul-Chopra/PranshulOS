/**
 * electron/main.js — PranshulOS desktop shell
 *
 * Responsibilities:
 * 1. Spawn the Flask backend (python main.py or the bundled exe)
 * 2. Poll localhost:5000/api/ping until Flask is ready
 * 3. Open a BrowserWindow pointing at localhost:5000/home
 * 4. Check GitHub Releases for updates via electron-updater; prompt to restart when ready
 * 5. Kill Flask when the window closes
 */

const { app, BrowserWindow, shell, dialog, ipcMain } = require('electron');
const { spawn }      = require('child_process');
const path           = require('path');
const http           = require('http');
const { autoUpdater } = require('electron-updater');

let mainWindow   = null;
let flaskProcess = null;

// ── Auto-updater setup ────────────────────────────────────────────────────────

function setupAutoUpdater() {
  // Only run in the packaged app — no-op in dev (avoids noisy errors).
  if (!app.isPackaged) return;

  // Don't auto-install silently; let the user choose when to restart.
  autoUpdater.autoInstallOnAppQuit = true;
  autoUpdater.autoDownload = true;

  autoUpdater.on('update-available', (info) => {
    // Optional: you could show a "Downloading update…" toast here.
    console.log(`Update available: ${info.version} — downloading in background.`);
  });

  autoUpdater.on('update-downloaded', (info) => {
    // Update is fully downloaded. Ask user whether to restart now.
    dialog.showMessageBox(mainWindow, {
      type: 'info',
      title: 'Update ready',
      message: `PranshulOS ${info.version} is ready to install.`,
      detail: 'Restart now to apply the update, or it will install automatically next time you close the app.',
      buttons: ['Restart now', 'Later'],
      defaultId: 0,
      cancelId: 1,
    }).then(({ response }) => {
      if (response === 0) {
        autoUpdater.quitAndInstall();
      }
    });
  });

  autoUpdater.on('error', (err) => {
    // Log but never surface to the user — update is non-critical.
    console.error('Auto-updater error:', err.message);
  });

  // Check immediately on launch, then every 4 hours while the app is open.
  autoUpdater.checkForUpdates().catch(() => {});
  setInterval(() => {
    autoUpdater.checkForUpdates().catch(() => {});
  }, 4 * 60 * 60 * 1000);
}

// ── Start Flask ───────────────────────────────────────────────────────────────

function startFlask() {
  const isDev = !app.isPackaged;

  let cmd, args, cwd;

  if (isDev) {
    cmd  = process.platform === 'win32' ? 'python' : 'python3';
    args = ['main.py'];
    cwd  = path.join(__dirname, '..');
  } else {
    cmd  = path.join(process.resourcesPath, 'flask', 'flask.exe');
    args = [];
    cwd  = path.join(process.resourcesPath, 'flask');
  }

  flaskProcess = spawn(cmd, args, {
    cwd,
    stdio: 'ignore',
    windowsHide: true,
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
    autoHideMenuBar: true,
  });

  mainWindow.loadURL('http://127.0.0.1:5000/');

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
    setupAutoUpdater();   // ← runs after window exists so dialog has a parent
  } catch (err) {
    console.error('Could not connect to Flask:', err.message);
    app.quit();
  }
});

app.on('window-all-closed', () => {
  if (flaskProcess) {
    flaskProcess.kill();
    flaskProcess = null;
  }
  app.quit();
});

app.on('activate', async () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    try {
      await waitForFlask(10, 200);
      createWindow();
    } catch (_) {}
  }
});