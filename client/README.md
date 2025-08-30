# Hiresify Frontend

Hiresify Frontend is a web client built with **React + TypeScript + Vite**.  
It integrates with the Hiresify Engine backend to provide authentication, media
upload, and user-facing workflows.

---

## Features

- ⚛️ **React + TypeScript** with modern hooks and Redux Toolkit
- ⚡ **Vite** for fast builds and hot module replacement
- 🔐 OAuth2 / PKCE authentication flow
- 📂 File upload UI with chunked/resumable support
- 🧪 Testing with Vitest and React Testing Library
- 🎨 Prettier + ESLint for consistent code style

---

## Project Structure

```
client/
├── index.html              # Entry point
├── vite.config.ts          # Vite configuration
├── package.json            # Dependencies & scripts
├── src/
│   ├── App.tsx             # Main App component
│   ├── main.tsx            # React DOM bootstrap
│   ├── app/                # Redux store & slices
│   ├── api/                # API client wrappers
│   ├── view/               # Page components (Home, Login, Register, etc.)
│   ├── feature/blob/       # File upload state management
│   ├── tool/               # PKCE & helper utilities
│   ├── testing/            # Test utilities & mock server
│   └── assets/             # Static assets (images, etc.)
```

---

## Getting Started

### 1. Install Dependencies

```bash
cd client
npm install
```

### 2. Configure Environment

Create a `.env` file in `client/`:

```
VITE_API_BASE_URL=http://localhost:8000
VITE_CLIENT_ID=your-client-id
VITE_REDIRECT_URI=http://localhost:5173/login/callback
```

### 3. Run Development Server

```bash
npm run dev
```

Visit: [http://localhost:5173](http://localhost:5173)

### 4. Build for Production

```bash
npm run build
npm run preview
```

---

## Testing

```bash
npm run test
```

Uses **Vitest** + **React Testing Library**.

---

## License

MIT. See [LICENSE](../LICENSE).
