import { Link } from "react-router";
import { SignupForm } from "wasp/client/auth";
import { AuthLayout } from "./AuthLayout";

export function SignupPage() {
  return (
    <AuthLayout>
      <div className="text-center mb-8">
        <h1 className="text-3xl font-black tracking-tighter mb-2">VIBE2BLENDER</h1>
        <p className="text-accent text-[10px] uppercase tracking-widest font-bold">CREATE_ACCOUNT</p>
      </div>

      <SignupForm 
        appearance={{
          colors: {
            brand: '#000000',
            brandAccent: '#333333',
          },
        }}
      />

      <div className="mt-8 pt-6 border-t border-border text-center">
        <span className="text-[10px] font-bold text-accent uppercase tracking-widest">
          ALREADY REGISTERED?{" "}
          <Link to="/login" className="text-text underline hover:text-accent transition-colors ml-2">
            LOG_IN
          </Link>
        </span>
      </div>
    </AuthLayout>
  );
}
