import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";
import { z } from "zod";
import { useOrganisationDirectory } from "@/api/hooks";
import { apiErrorMessage, useAuth } from "@/lib/auth";

const schema = z
  .object({
    name: z.string().min(2, "Enter your full name"),
    email: z.string().email("Enter a valid email"),
    password: z.string().min(8, "At least 8 characters"),
    orgName: z.string().min(2, "Enter your organisation name"),
    sector: z.enum(["healthcare", "education", "local_government", "finance", "generic"]),
    language: z.enum(["en", "hi"]),
    isSubOrganisation: z.boolean(),
    parentOrganisationId: z.string().optional(),
  })
  .superRefine((values, ctx) => {
    if (values.isSubOrganisation && !values.parentOrganisationId) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["parentOrganisationId"],
        message: "Select the existing organisation this is a sub-organisation of",
      });
    }
  });
type FormValues = z.infer<typeof schema>;

export default function Register() {
  const { register: doRegister } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"details" | "parent">("details");
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { sector: "generic", language: "en", isSubOrganisation: false },
  });

  const isSubOrganisation = watch("isSubOrganisation");
  const { data: directory, isLoading: directoryLoading } = useOrganisationDirectory(isSubOrganisation);

  useEffect(() => {
    if (!isSubOrganisation) setActiveTab("details");
  }, [isSubOrganisation]);

  async function onSubmit(values: FormValues) {
    setError(null);
    try {
      await doRegister({
        name: values.name,
        email: values.email,
        password: values.password,
        organisation: {
          name: values.orgName,
          sector: values.sector,
          parent_organisation_id: values.isSubOrganisation ? values.parentOrganisationId : undefined,
        },
        language: values.language,
      });
      navigate("/overview");
    } catch (e) {
      setError(apiErrorMessage(e));
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-bg px-4 py-10">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="text-accent-ink font-bold text-2xl tracking-tight">RRI</div>
          <div className="text-xs text-muted uppercase tracking-widest mt-1">Ransomware Readiness Index</div>
        </div>
        <form onSubmit={handleSubmit(onSubmit)} className="card space-y-4">
          <h1 className="text-lg font-medium text-light">Register your organisation</h1>

          <div>
            <label className="label-text" htmlFor="name">Your name</label>
            <input id="name" className="input-field mt-1" {...register("name")} />
            {errors.name && <p className="text-xs text-red-400 mt-1">{errors.name.message}</p>}
          </div>
          <div>
            <label className="label-text" htmlFor="email">Work email</label>
            <input id="email" className="input-field mt-1" type="email" {...register("email")} />
            {errors.email && <p className="text-xs text-red-400 mt-1">{errors.email.message}</p>}
          </div>
          <div>
            <label className="label-text" htmlFor="password">Password</label>
            <input id="password" className="input-field mt-1" type="password" {...register("password")} />
            {errors.password && <p className="text-xs text-red-400 mt-1">{errors.password.message}</p>}
          </div>
          <div className="flex items-center gap-2 pt-1">
            <input id="isSubOrganisation" type="checkbox" {...register("isSubOrganisation")} />
            <label className="label-text" htmlFor="isSubOrganisation">
              This is a sub-organisation of an existing organisation
            </label>
          </div>

          {isSubOrganisation && (
            <div className="flex gap-1 border-b border-border">
              <button
                type="button"
                onClick={() => setActiveTab("details")}
                className={`px-3 py-1.5 text-xs font-medium uppercase tracking-wide ${
                  activeTab === "details" ? "text-accent-ink border-b-2 border-accent" : "text-muted"
                }`}
              >
                Organisation Details
              </button>
              <button
                type="button"
                onClick={() => setActiveTab("parent")}
                className={`px-3 py-1.5 text-xs font-medium uppercase tracking-wide ${
                  activeTab === "parent" ? "text-accent-ink border-b-2 border-accent" : "text-muted"
                }`}
              >
                Parent Organisation
              </button>
            </div>
          )}

          <div className={isSubOrganisation && activeTab !== "details" ? "hidden" : "space-y-4"}>
            <div>
              <label className="label-text" htmlFor="orgName">Organisation name</label>
              <input id="orgName" className="input-field mt-1" {...register("orgName")} />
              {errors.orgName && <p className="text-xs text-red-400 mt-1">{errors.orgName.message}</p>}
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="label-text" htmlFor="sector">Sector</label>
                <select id="sector" className="input-field mt-1" {...register("sector")}>
                  <option value="generic">Generic / Other</option>
                  <option value="healthcare">Healthcare</option>
                  <option value="education">Education</option>
                  <option value="local_government">Local Government</option>
                  <option value="finance">Finance</option>
                </select>
              </div>
              <div>
                <label className="label-text" htmlFor="language">Language</label>
                <select id="language" className="input-field mt-1" {...register("language")}>
                  <option value="en">English</option>
                  <option value="hi">हिन्दी</option>
                </select>
              </div>
            </div>
          </div>

          {isSubOrganisation && (
            <div className={activeTab !== "parent" ? "hidden" : ""}>
              <label className="label-text" htmlFor="parentOrganisationId">Parent organisation</label>
              <select id="parentOrganisationId" className="input-field mt-1" {...register("parentOrganisationId")}>
                <option value="">{directoryLoading ? "Loading…" : "Select an organisation"}</option>
                {directory?.map((org) => (
                  <option key={org.id} value={org.id}>{org.name}</option>
                ))}
              </select>
              {errors.parentOrganisationId && (
                <p className="text-xs text-red-400 mt-1">{errors.parentOrganisationId.message}</p>
              )}
              <p className="text-xs text-muted mt-2">
                Your registration will be sent to this organisation for verification. You won't be able to complete
                an assessment until they verify you from their Integrity Ledger.
              </p>
            </div>
          )}

          {error && <p className="text-xs text-red-400">{error}</p>}
          <button className="btn-primary w-full" disabled={isSubmitting}>
            {isSubmitting ? "Creating account…" : "Create account"}
          </button>
          <p className="text-xs text-muted text-center">
            Already have an account? <Link to="/login" className="text-accent-ink">Sign in</Link>
          </p>
        </form>
      </div>
    </div>
  );
}
