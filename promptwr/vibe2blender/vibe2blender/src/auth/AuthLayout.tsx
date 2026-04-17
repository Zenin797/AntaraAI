import { ReactNode } from "react";

export function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex justify-center items-center min-h-[calc(100vh-100px)]">
      <div className="bg-secondary border border-border w-full max-w-md px-8 py-10">
        {children}
      </div>
    </div>
  );
}
