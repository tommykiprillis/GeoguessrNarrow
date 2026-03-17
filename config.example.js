/**
 * Configuration for frontend API endpoints
 * This file is for reference. The configuration is handled in script.js
 *
 * Development: Uses window.location.origin (same server)
 * Production: Uses your Render backend URL
 */

// Development (localhost or same-origin)
// const API_BASE_URL = window.location.origin;

// Production (GitHub Pages pointing to Render)
// const API_BASE_URL = 'https://geoguessr-narrower.onrender.com';

// Auto-detect (used in script.js)
const API_BASE_URL =
    window.location.hostname === "localhost" ||
    window.location.hostname === "127.0.0.1"
        ? window.location.origin
        : "https://geoguessr-narrower.onrender.com"; // Replace with your Render URL
