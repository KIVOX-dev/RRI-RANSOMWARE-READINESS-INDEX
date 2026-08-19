import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { AuthProvider } from "@/lib/auth";

vi.mock("@/api/client", () => ({
  AuthAPI: { me: vi.fn().mockRejectedValue(new Error("no session")) },
}));

function renderWithProviders() {
  const client = new QueryClient();
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={["/dashboard"]}>
        <AuthProvider>
          <Routes>
            <Route path="/login" element={<div>Login Page</div>} />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <div>Dashboard Content</div>
                </ProtectedRoute>
              }
            />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>
  );
}

describe("ProtectedRoute", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("redirects unauthenticated users to /login", async () => {
    renderWithProviders();
    await waitFor(() => expect(screen.getByText("Login Page")).toBeInTheDocument());
    expect(screen.queryByText("Dashboard Content")).not.toBeInTheDocument();
  });
});
