// Requires frontend/.env.local with:
// VITE_AUTH0_DOMAIN=your-tenant.auth0.com
// VITE_AUTH0_AUDIENCE=your-api-audience

import { Auth0Provider } from "@auth0/auth0-react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import JobStatus from "./pages/JobStatus";

export default function App() {
  return (
    <Auth0Provider
      domain={import.meta.env.VITE_AUTH0_DOMAIN}
      clientId={import.meta.env.VITE_AUTH0_CLIENT_ID}
      authorizationParams={{
        redirect_uri: window.location.origin,
        audience: import.meta.env.VITE_AUTH0_AUDIENCE,
      }}
    >
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/jobs/:job_id" element={<JobStatus />} />
        </Routes>
      </BrowserRouter>
    </Auth0Provider>
  );
}
