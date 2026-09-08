# VibeForGood2026
#NgYanHerng 

A starter with a Node.js backend and a plain HTML, CSS, and JavaScript frontend.
No third-party packages, Python, or uv are required.

## Start developing

Use Node.js 22 or newer (which includes npm). From this project directory, run:

```bash
npm run dev
```

Open http://127.0.0.1:3000. The page checks `/api/health` to confirm the frontend
can reach the backend. The backend restarts when its code changes; refresh the
browser after editing frontend files. Stop the server with Ctrl+C.

There are no dependencies to install and no frontend build step.

## Files

```text
backend/
  server.js       HTTP server, API routes, and frontend asset serving
frontend/
  index.html      Page structure
  styles.css      Page styling
  app.js          Browser logic and API connection
package.json      Commands and Node.js requirement
.gitignore        Files excluded from Git
README.md         Setup and development instructions
```

Add backend API routes in `backend/server.js` before the asset lookup. Add UI
in `frontend/index.html`, styling in `frontend/styles.css`, and interactions in
`frontend/app.js`. When adding new frontend assets, register their URL, filename,
and content type in the server's `assets` map.

## Commands

```bash
npm run dev     # Start with automatic backend restarts
npm start       # Start without watching files
npm run check   # Check backend and frontend JavaScript syntax
```

The server binds to `127.0.0.1:3000` by default. To use another port:

```bash
PORT=3001 npm run dev
```

`HOST` can also be set through the shell. Environment files are not loaded
automatically. Keep secrets in backend environment variables, never frontend code.

This starter provides an API connection and static page. Add persistence,
authentication, and application-specific features as your project needs them.

## Working together (branch + PR convention)

Two people work off `main` — never commit to it directly.

1. Sync, then branch off `main` for each piece of work:

   ```bash
   git checkout main
   git pull
   git checkout -b <your-name>/<feature>   # e.g. braed/medication-endpoint
   ```

2. Commit as you go, then push and open a pull request:

   ```bash
   git push -u origin <your-name>/<feature>
   ```

3. The other person reviews the PR and merges it into `main`, then deletes the branch.

4. Stay in sync — before starting work and before pushing:

   ```bash
   git pull origin main
   git merge main        # or: git rebase main
   ```

The backend is a single `backend/server.js`. To avoid constant merge conflicts,
split routes into their own modules (e.g. `backend/routes/medication.js`) and keep
`server.js` a thin router. Each laptop runs `npm run dev` on its own machine.
