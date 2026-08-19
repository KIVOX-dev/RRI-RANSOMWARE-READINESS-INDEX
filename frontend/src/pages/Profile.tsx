import { Layout } from "@/components/Layout";
import { useAuth } from "@/lib/auth";

export default function Profile() {
  const { user } = useAuth();

  return (
    <Layout title="Profile">
      <div className="card max-w-md space-y-3">
        <div>
          <div className="label-text">Name</div>
          <div className="text-light text-sm mt-1">{user?.name}</div>
        </div>
        <div>
          <div className="label-text">Email</div>
          <div className="text-light text-sm mt-1">{user?.email}</div>
        </div>
        <div>
          <div className="label-text">Role</div>
          <div className="text-light text-sm mt-1 capitalize">{user?.role.replace("_", " ")}</div>
        </div>
        <div>
          <div className="label-text">Language</div>
          <div className="text-light text-sm mt-1">{user?.language === "hi" ? "हिन्दी" : "English"}</div>
        </div>
      </div>
    </Layout>
  );
}
