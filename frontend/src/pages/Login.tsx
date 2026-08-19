import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";
import { z } from "zod";
import { apiErrorMessage, useAuth } from "@/lib/auth";

const schema = z.object({
  email: z.string().email("Enter a valid email"),
  password: z.string().min(1, "Password is required"),
});
type FormValues = z.infer<typeof schema>;

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  async function onSubmit(values: FormValues) {
    setError(null);
    try {
      await login(values.email, values.password);
      navigate("/overview");
    } catch (e) {
      setError(apiErrorMessage(e));
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-bg px-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <div className="text-accent-ink font-bold text-2xl tracking-tight">RRI</div>
          <div className="text-xs text-muted uppercase tracking-widest mt-1">Ransomware Readiness Index</div>
        </div>
        <form onSubmit={handleSubmit(onSubmit)} className="card space-y-4">
          <h1 className="text-lg font-medium text-light">Sign in</h1>
          <div>
            <label className="label-text" htmlFor="email">Email</label>
            <input id="email" className="input-field mt-1" type="email" {...register("email")} />
            {errors.email && <p className="text-xs text-red-400 mt-1">{errors.email.message}</p>}
          </div>
          <div>
            <label className="label-text" htmlFor="password">Password</label>
            <input id="password" className="input-field mt-1" type="password" {...register("password")} />
            {errors.password && <p className="text-xs text-red-400 mt-1">{errors.password.message}</p>}
          </div>
          {error && <p className="text-xs text-red-400">{error}</p>}
          <button className="btn-primary w-full" disabled={isSubmitting}>
            {isSubmitting ? "Signing in…" : "Sign in"}
          </button>
          <p className="text-xs text-muted text-center">
            No account? <Link to="/register" className="text-accent-ink">Register your organisation</Link>
          </p>
        </form>
      </div>
    </div>
  );
}
