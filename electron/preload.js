/**
 * electron/preload.js
 *
 * Runs in the renderer process before page scripts load.
 * With contextIsolation: true, this is the only place where
 * Node.js APIs can be safely exposed to the page if needed.
 *
 * Currently empty — all communication goes through Flask's HTTP API
 * (fetch('/launch/...'), fetch('/api/...')) so no Node bridge is needed.
 * This file exists as a placeholder for future use (e.g. exposing
 * a native notification API or file system access).
 */

// Nothing to expose yet — Flask handles everything via HTTP.
