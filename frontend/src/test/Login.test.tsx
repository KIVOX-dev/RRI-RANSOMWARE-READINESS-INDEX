import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import { AuthProvider } from "@/lib/auth";
import Login from "@/pages/Login";

vi.mock("@/api/client", () => ({
  AuthAPI: { me: vi.fn().mockRejectedValue(new Error("no session")), login: vi.fn() },
}));

function renderLogin() {
  const client = new QueryClient();
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter>
        <AuthProvider>
          <Login />
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>
  );
}

describe("Login form validation", () => {
  it("shows a validation error for an invalid email", async () => {
    renderLogin();
    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    fireEvent.input(emailInput, { target: { value: "not-an-email" } });
    fireEvent.input(passwordInput, { target: { value: "x" } });
    fireEvent.submit(screen.getByRole("button", { name: /sign in/i }).closest("form")!);

    await waitFor(
      () => expect(screen.getByText(/enter a valid email/i)).toBeInTheDocument(),
      { timeout: 3000 }
    );
  });
});
